import { AuthProvider } from './contexts/AuthContext';
import Login from './components/Login';
import './App.css'

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Login />
      </div>
    </AuthProvider>
  );
}

export default App;
