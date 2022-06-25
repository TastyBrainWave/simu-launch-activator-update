using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor.XR.LegacyInputHelpers;

public class KeepInfront : MonoBehaviour
{
    public float speed;
    private float offset;
    private Quaternion target;

    private void Start()
    {
        //offset = gameObject.GetComponent<CameraOffset>().cameraYOffset;
    }

    private void Update()
    {
        gameObject.transform.position = new Vector3(Camera.main.transform.position.x, 1.3f, Camera.main.transform.position.z);
        Vector3 targetY = new Vector3(0, Camera.main.transform.eulerAngles.y, 0);
        target = Quaternion.Euler(targetY);
        gameObject.transform.rotation = Quaternion.Lerp(gameObject.transform.rotation, target, speed * Time.deltaTime);

       
    }

}
