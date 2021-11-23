using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public class AgentData
{
    public List<Vector3> positions;
}

public class AgentController : MonoBehaviour
{
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getRobots";
    string getboxEndpoint = "/getBoxes";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    string end= "/finish";
    AgentData robotsData, boxData;
    GameObject[] agents;
    GameObject[] boxes;
    List<Vector3> oldPositions;
    List<Vector3> oldPositionsBoxes;
    List<Vector3> newPositions;
    // Pause the simulation while we get the update from the server
    bool hold = false;
    int piled=0;
    public GameObject robotPrefab, boxPrefab, rackPrefab, floor;
    public int NAgents, width, height;
    public float density;
    public float timeToUpdate = 5.0f, timer, dt;

    void Start()
    {
        robotsData = new AgentData();
        boxData = new AgentData();
        oldPositions = new List<Vector3>();
        newPositions = new List<Vector3>();

        agents = new GameObject[NAgents];

        floor.transform.localScale = new Vector3((float)width/10, 1, (float)height/10);
        floor.transform.localPosition = new Vector3((float)width/2-0.5f, 0, (float)height/2-0.5f);
        
        timer = timeToUpdate;
        Instantiate(rackPrefab, new Vector3(0,0.5f,0), Quaternion.identity);

        for(int i = 0; i < NAgents; i++)
            agents[i] = Instantiate(robotPrefab, Vector3.zero, Quaternion.identity);

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
                
                Vector3 dir = oldPositions[s] - newPositions[s];
                agents[s].transform.rotation = Quaternion.LookRotation(dir);
                
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
            StartCoroutine(updateboxData());
            StartCoroutine(checkStop());
        }
    }

    IEnumerator checkStop()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + end);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            Debug.Log(www.downloadHandler.text);
            if (www.downloadHandler.text=="0"){
                
                EditorApplication.isPlaying = false;
            }
        }
    }

    IEnumerator SendConfiguration(){
        WWWForm form = new WWWForm();

        form.AddField("NAgents", NAgents.ToString());
        form.AddField("width", width.ToString());
        form.AddField("height", height.ToString());
        form.AddField("density", density.ToString());

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
            StartCoroutine(GetboxData());
        }
    }

    IEnumerator GetAgentData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            robotsData = JsonUtility.FromJson<AgentData>(www.downloadHandler.text);

            // Store the old positions for each agent
            oldPositions = new List<Vector3>(newPositions);

            newPositions.Clear();

            foreach(Vector3 v in robotsData.positions)
                newPositions.Add(v);
            hold=false;
        }

        
    }

    IEnumerator GetboxData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getboxEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            boxData = JsonUtility.FromJson<AgentData>(www.downloadHandler.text);
            boxes = new GameObject[boxData.positions.Count];
            int j=0;
            foreach(Vector3 position in boxData.positions)
            {
                boxes[j]=Instantiate(boxPrefab, position, Quaternion.identity);
                j+=1;
            }
        }
    }

    IEnumerator updateboxData() 
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getboxEndpoint);
        yield return www.SendWebRequest();
        Vector3 deposito= new Vector3(0,0.5f,0);
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {   

            boxData = JsonUtility.FromJson<AgentData>(www.downloadHandler.text);
            foreach(GameObject box in boxes)
            {
                
                bool picked=true;
                foreach(Vector3 position in boxData.positions){
                    if (position== box.transform.position){
                        picked=false;
                        break;
                    }
                }
                if (picked && box.transform.position!= deposito){
                    box.GetComponent<Renderer>().enabled = false;
                }

            }
        }
    }
}
