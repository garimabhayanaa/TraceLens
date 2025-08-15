export const testBackendConnection = async () => {
  const BACKEND_URL="https://tracelens.onrender.com"
  try {
    const response = await fetch(`${BACKEND_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Backend connection successful:', data);
      return { success: true, data };
    } else {
      console.error('❌ Backend connection failed:', response.status);
      return { success: false, error: `HTTP ${response.status}` };
    }
  } catch (error) {
    console.error('❌ Network error:', error);
    return { success: false, error: 'Network error' };
  }
};
