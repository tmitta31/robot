// DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited.

// This material is based upon work supported by the Under Secretary of Defense for 
// Research and Engineering under Air Force Contract No. FA8702-15-D-0001. Any opinions,
// findings, conclusions or recommendations expressed in this material are those 
// of the author(s) and do not necessarily reflect the views of the Under 
// Secretary of Defense for Research and Engineering.

// © 2023 Massachusetts Institute of Technology.

// Subject to FAR52.227-11 Patent Rights - Ownership by the contractor (May 2014)

// The software/firmware is provided to you on an As-Is basis

// Delivered to the U.S. Government with Unlimited Rights, as defined in DFARS Part 
// 252.227-7013 or 7014 (Feb 2014). Notwithstanding any copyright notice, 
// U.S. Government rights in this work are defined by DFARS 252.227-7013 or 
// DFARS 252.227-7014 as detailed above. Use of this work other than as specifically
// authorized by the U.S. Government may violate any copyrights that exist in this work.

using System;
using System.IO;
using UnityEngine;

public class SupportFuncs : MonoBehaviour
{
    private static string startPath = Application.dataPath; 
    private const string targetFolderName = "launch"; 
    private const string targetFileName = "address"; 
    private static string foundPath; 

    void Start()
    {
        foundPath = TraverseUpToFindFolder(startPath, targetFolderName);
    }

    public static string GetWebUrlFromConfig()
    {
        if (foundPath == null)
        {
            foundPath = TraverseUpToFindFolder(startPath, targetFolderName);
        }

        if (foundPath != null)
        {
            string filePath = Path.Combine(foundPath, targetFileName);

            string text = ReadTextFromFile(filePath);

            return text?.Trim();
        }

        return null;
    }

    public static string TraverseUpToFindFolder(string startPath, string targetFolderName)
    {
        DirectoryInfo currentDir = new DirectoryInfo(startPath);
        
        while (currentDir != null)
        {
            foreach (var dir in currentDir.GetDirectories())
            {
                if (dir.Name == targetFolderName)
                {
                    return dir.FullName;
                }
            }

            currentDir = currentDir.Parent;
        }

        return null;
    }

    public static string ReadTextFromFile(string path)
    {
        if (File.Exists(path))
        {
            try
            {
                using (StreamReader reader = new StreamReader(path))
                {
                    return reader.ReadToEnd();
                }
            }
            catch (Exception e)
            {
                Debug.LogError("An error occurred while reading the file: " + e.Message);
                return null;
            }
        }
        else
        {
            Debug.LogError("File not found at " + path);
            return null;
        }
    }

    public static Vector2 ExtractTupleFromString(string strVal)
    {
        int start = strVal.IndexOf('(') + 1;
        int end = strVal.IndexOf(')');
        
        if (start == -1 || end == -1 || start >= end)
        {
            // Handle the case when the string doesn't contain a valid tuple
            return Vector2.zero;
        }

        string numbersStr = strVal.Substring(start, end - start);
        string[] numbers = numbersStr.Split(',');

        if (numbers.Length != 2)
        {
            // Handle the case when there are not exactly two elements in the tuple
            return Vector2.zero;
        }

        float x, y;
        if (float.TryParse(numbers[0].Trim(), out x) && float.TryParse(numbers[1].Trim(), out y))
        {
            return new Vector2(x, y);
        }
        else
        {
            // Handle the case when the numbers are not valid floats
            return Vector2.zero;
        }
    }
}
