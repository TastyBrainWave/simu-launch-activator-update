using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.Android;


public class LoadImage : MonoBehaviour
{

    public string FilePath;
    public Texture2D DefaultTexture;
    private Texture2D _texture;
    private SpriteRenderer _sr;

 

    IEnumerator Start()
    { 
    //    if (!Permission.HasUserAuthorizedPermission(Permission.ExternalStorageRead))
    //Permission.RequestUserPermission(Permission.ExternalStorageRead);
        using (UnityWebRequest loader = UnityWebRequestTexture.GetTexture("file://" + FilePath))
        {
            yield return loader.SendWebRequest();

            if (string.IsNullOrEmpty(loader.error))
            {
                _texture = DownloadHandlerTexture.GetContent(loader);
                ReplaceImage(_texture);
            }
            else
            {
                Debug.LogErrorFormat("Error loading Texture '{0}': {1}", loader.uri, loader.error);
               
                ReplaceImage(null);
            }
        }
    }

    void ReplaceImage(Texture2D t2d)
    {
        if (_sr == null)
        {
            _sr = GetComponent<SpriteRenderer>();
        }
        if(t2d == null)
        {
            _texture = DefaultTexture;
        }
        Sprite s = Sprite.Create(_texture, new Rect(0.0f, 0.0f, _texture.width, _texture.height), new Vector2(0.5f, 0.5f), 100.0f);
        _sr.sprite = s;
    }
}
