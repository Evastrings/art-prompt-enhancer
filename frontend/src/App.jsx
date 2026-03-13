import { useState } from 'react'

import './App.css'

function App() {
  // const [count, setCount] = useState(0)
  const [prompt, setPrompt] = useState("")
  const [model, setModel] = useState("SD 1.5")
  const [im_model, setImModel] = useState("Midjourney")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [selectedFile, setSelectedFile] = useState(null)
  const [imageResult, setImageResult] = useState(null)
  const [imageLoading, setImageLoading] = useState(false)

  const handleSubmit = async ()=> {
    setLoading(true)
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json'},
        body: JSON.stringify({ prompt: prompt, model: model })
      })

      const data = await response.json();
      console.log('Prompts recieved:', data);
      setResult(data);
    }
    
    catch (error) {
      console.error('Error generating prompt:', error);
      alert('Failed to enhance prompt, Make sure your backend is running');
    }

    
    finally {
      setLoading(false);
    }

  }
  
   //Clipboard
  const handleCopy = async (text, type) => {
    await navigator.clipboard.writeText(text)
    setCopied(type);
    setTimeout(() => setCopied(false), 2000);
  };


  const handleImageSubmit = async () => {
    if (!selectedFile) {
      alert('Please select an image first');
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      alert('Image must be under 10MB');
      return;
    }
    setImageLoading(true)
    

     // Upload Image
  try {
    const formData = new FormData();
    formData.append('file', selectedFile)
    formData.append('model', im_model)

    const response = await fetch(`${import.meta.env.VITE_API_URL}/upload`, {
      method: 'POST',
      body: formData
    
      
    });
   

    const data = await response.json();
    console.log('Prompts recieved:', data);

    setImageResult(data);
  }

    catch (error) {
      console.error('Error analyzing image:', error);
      alert('Failed to analyze image');
    } finally {
      setImageLoading(false);
    } 
};

 
  return (
    <>
      <h1> Hey there, Artist</h1>
      <form>
        <label> Enter rough prompt:
          <input type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
           />
        </label>
      </form>

      <select
        value={model}
        onChange={(e) => setModel(e.target.value)}
      >
        <option>SD 1.5</option>
        <option>SDXL</option>
        <option>SD 3</option>
        <option> Midjourney</option>
        <option>Flux</option>
      </select>
      <button onClick={handleSubmit} disabled={!prompt.trim()}>Submit</button>

      {loading && <p>Enhancing your prompt...</p>}
      {result && (
        <div>
          <p onClick={() => handleCopy(result.positive_prompt, 'positive')}>{result.positive_prompt} {copied === 'positive' && <span> <br />Copied </span> } </p>
          <p onClick={() => handleCopy(result.negative_prompt, 'negative')}> {result.negative_prompt} {copied === 'negative' && <span> <br />Copied </span> } </p>
        </div>
      )}

        {/*NEW PAGE FOR UPLOADING IMAGE*/}
        <h1> Hey there, Image Artist</h1>
      <form>
        <label> Enter Image to extract prompt:
          <input type="file"
            accept="image/*"
            onChange={(e) => setSelectedFile(e.target.files[0])}
           />
        </label>
      </form>

      <select
        value={im_model}
        onChange={(e) => setImModel(e.target.value)}
      >
        <option>SD 1.5</option>
        <option>SDXL</option>
        <option>SD 3</option>
        <option> Midjourney</option>
        <option>Flux</option>
      </select>
      <button onClick={handleImageSubmit} disbled={!selectedFile}>Submit</button>

      {imageLoading && <p>Diffusing Prompt for your Image...</p>}
      {imageResult && (
        <div>
          <p onClick={() => handleCopy(imageResult.positive_prompt, 'positive')}>{imageResult.positive_prompt} {copied === 'positive' && <span> <br />Copied </span> } </p>
          <p onClick={() => handleCopy(imageResult.negative_prompt, 'negative')}> {imageResult.negative_prompt} {copied === 'negative' && <span> <br />Copied </span> } </p>
        </div>
      )}
    </>
  )
}

export default App
