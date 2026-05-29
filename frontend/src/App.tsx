import { BrowserRouter } from 'react-router-dom';
import { AppDataProvider } from './context/AppDataContext';
import { AppRouter } from './router';

function App() {
  return (
    <AppDataProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </AppDataProvider>
  );
}

export default App;
