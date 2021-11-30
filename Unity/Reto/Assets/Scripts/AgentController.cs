using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public class AgentData
{
    public List<Vector3> positions;

    public List<Vector3> data;
}

public class AgentController : MonoBehaviour
{
    string serverUrl = "http://localhost:8585";
    string getCarsEndpoint = "/getCars";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    string end= "/finish";
    AgentData carData;
    GameObject[] agents;
    List<Vector3> oldPositions;
    List<Vector3> newPositions;

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
        oldPositions = new List<Vector3>();
        newPositions = new List<Vector3>();
        oldPositionsData = new List<Vector3>();
        newPositionsData = new List<Vector3>();

        agents = new GameObject[NAgents];

        
        timer = timeToUpdate;

        for(int i = 0; i < NAgents; i++)
            agents[i] = Instantiate(carPrefab, Vector3.zero, Quaternion.identity);

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
                for(int aa=0; aa<agents.Length; aa++){
                    if (oldPositionsData[s].x==newPositionsData[aa].x){
                        Vector3 interpolated = Vector3.Lerp(oldPositions[s], newPositions[aa], dt);
                        agents[s].transform.localPosition = interpolated;
                    
                        Vector3 dir = oldPositions[s] - newPositions[aa];
                        agents[s].transform.rotation = Quaternion.LookRotation(-dir);
                        break;
                    }
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
        }
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
}
