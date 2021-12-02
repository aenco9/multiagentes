using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;
using System.Linq;

public class AgentData
{
    public List<Vector3> positions;

    public List<Vector3> data;
}

public class LightData
{
    public List<Vector3> positions;

}

public class AgentController : MonoBehaviour
{
    string serverUrl = "http://localhost:8585";
    //string serverUrl="https://multiagentese1.mybluemix.net";
    string getCarsEndpoint = "/getCars";
    string getTrafficEndpoint = "/getTrafficLights";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    string end= "/finish";
    AgentData carData;
    LightData trafficLightData;
    GameObject[] agents;
    List<Vector3> oldPositions;
    List<Vector3> newPositions;
    public GameObject[] trafficLights;

    List<Vector3> oldPositionsData;
    List<Vector3> newPositionsData;
    // Pause the simulation while we get the update from the server
    bool hold = false;
    public GameObject carPrefab;
    public int NAgents;

    public float timeToUpdate = 5.0f, timer, dt;

    void Start()
    {
        carData = new AgentData();
        trafficLightData = new LightData();
        oldPositions = new List<Vector3>();
        newPositions = new List<Vector3>();
        oldPositionsData = new List<Vector3>();
        newPositionsData = new List<Vector3>();

        agents = new GameObject[NAgents];
        
        
        timer = timeToUpdate;

        for(int i = 0; i < NAgents; i++){
            agents[i] = Instantiate(carPrefab, Vector3.zero, Quaternion.identity);
            agents[i].gameObject.name="Car" + i.ToString();
            agents[i].gameObject.transform.GetChild(0).GetComponent<Renderer>().material.SetColor("_Color", UnityEngine.Random.ColorHSV(0f, 1f, 1f, 1f, 0.5f, 1f));
        }

        StartCoroutine(SendConfiguration());
        
    }

    private void Update() 
    {
        float t = timer/timeToUpdate;
        // Smooth out the transition at start and end
        dt = t * t * ( 3f - 2f*t);

        if(timer >= timeToUpdate)
        {
            timer = 0;
            hold = true;
            StartCoroutine(UpdateSimulation());
        }
        
        if (!hold)
        {
            for (int s = 0; s < agents.Length; s++)
            {
                Vector3 interpolated = Vector3.Lerp(oldPositions[s], newPositions[s], dt);
                agents[s].transform.localPosition = interpolated;
                if(oldPositions[s]!=newPositions[s]){
                    Vector3 dir = oldPositions[s] - newPositions[s];
                    agents[s].transform.rotation = Quaternion.LookRotation(-dir);
                }
                

            }
            // Move time from the last frame
            timer += Time.deltaTime;
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetAgentData());
            StartCoroutine(GetTrafficData());
        }
    }

    IEnumerator SendConfiguration(){
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());

        UnityWebRequest www = UnityWebRequest.Post(serverUrl + sendConfigEndpoint, form);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");
            StartCoroutine(GetAgentData());
            StartCoroutine(GetTrafficData());
        }
        trafficLights = GameObject.FindGameObjectsWithTag("traffic");
    }

    IEnumerator GetAgentData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getCarsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            carData = JsonUtility.FromJson<AgentData>(www.downloadHandler.text);
            // Store the old positions for each agent
            oldPositions = new List<Vector3>(newPositions);
            oldPositionsData = new List<Vector3>(newPositionsData);
            newPositions.Clear();
            newPositionsData.Clear();

            foreach(Vector3 v in carData.positions)
                newPositions.Add(v);
            foreach(Vector3 v in carData.data)
                newPositionsData.Add(v);
            hold=false;
        }
    }

    IEnumerator GetTrafficData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            trafficLightData = JsonUtility.FromJson<LightData>(www.downloadHandler.text);
            // Store the old positions for each agent
            foreach(Vector3 v in trafficLightData.positions){
                foreach(GameObject trafficLight in trafficLights){
                    if(trafficLight.transform.position.x==v.x && trafficLight.transform.position.z==v.z){
                        if(v.y==9){
                            trafficLight.transform.GetChild(1).gameObject.GetComponent<Light>().enabled=true;
                            trafficLight.transform.GetChild(2).gameObject.GetComponent<Light>().enabled=false;
                        }else{
                            trafficLight.transform.GetChild(2).gameObject.GetComponent<Light>().enabled=true;
                            trafficLight.transform.GetChild(1).gameObject.GetComponent<Light>().enabled=false;
                        }
                    }
                }
            }
            hold=false;
        }
    }
}
