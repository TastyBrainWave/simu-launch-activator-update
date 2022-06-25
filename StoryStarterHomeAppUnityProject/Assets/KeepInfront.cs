using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor.XR.LegacyInputHelpers;

public class KeepInfront : MonoBehaviour
{
    private float offset;

    private void Start()
    {
        //offset = gameObject.GetComponent<CameraOffset>().cameraYOffset;
    }

    private void Update()
    {
        gameObject.transform.position = new Vector3(Camera.main.transform.position.x, 1.3f, Camera.main.transform.position.z);
        gameObject.transform.eulerAngles = new Vector3(0, Camera.main.transform.eulerAngles.y, 0);
    }

}
