// Basic health monitoring page
export default function Home() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>ABM Content Marketing Engine</h1>
      <p>Backend API Status: <a href="http://localhost:8000/health" target="_blank">Check Health</a></p>
      <p>API Documentation: <a href="http://localhost:8000/docs" target="_blank">View Docs</a></p>
    </div>
  );
}
