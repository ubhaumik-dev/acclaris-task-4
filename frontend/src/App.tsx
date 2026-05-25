import React from 'react'
import { useEffect,useState } from 'react'
import axios from 'axios'
import { useRef } from 'react'

interface FileItem{
  id: number,
  filename: string,
  filepath: string
}

const App = () => {
  const[files, setFiles] = useState<FileItem[]>([]);
  const[selectedFile, setSelectedFile] = useState<File| null>(null)
  const API = "http://127.0.0.1:8000";
  const fileInputRef = useRef<HTMLInputElement>(null)
  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) =>{
    if(e.target.files)
    {
       setSelectedFile(e.target.files[0])
    }
   
  }

  const fetchFiles = async() =>{
    try{
      const response = await axios.get(`${API}/get-files`)
      console.log(response);
      setFiles(response.data)
    }
    catch(error)
    {
      console.log(error)
    }
  }

  const deleteFile = async(id: number) =>{
    try{
      await axios.delete(
        `${API}/delete-file/${id}`
      )
      fetchFiles()
    }
    catch (error)
    {
      console.log(error)
    }
  }

  const uploadFile = async() =>{
    try{
      if(!selectedFile) return;
      const formData = new FormData()
      formData.append(
        "file",selectedFile
      )
      //console.log(selectedFile)
      const response = await axios.post(`${API}/upload-file`, formData)
      setSelectedFile(null)
      fetchFiles()
      if(fileInputRef.current){
        fileInputRef.current.value =""
      }
    }
    catch(error)
    {
      console.log(error)
    }
  }
  useEffect(() => {
   fetchFiles()
  }, [])
  
  return (
    <div>
      <h1>File Upload System</h1>
      <input type='file' onChange={onFileChange} ref={fileInputRef}/>
      <button onClick={()=>{uploadFile()}}>Upload</button>
      <hr/>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>File Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {
            files.map((file)=>(
              <tr key={file.id}>
                <td>{file.id}</td>
                <td>{file.filename}</td>
                <td>
                  <a href={`${API}/view-file/${file.id}`} target="_blank"><button>View</button></a>
                  <a href={`${API}/download-file/${file.id}`}><button>Download</button></a>
                  <button onClick={()=>{deleteFile(file.id)}}>Delete</button>
                </td>
              </tr>
            ))
          }
        </tbody>
      </table>
    </div>
  )
}

export default App