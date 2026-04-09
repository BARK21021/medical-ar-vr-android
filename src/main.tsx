import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomeView from './pages/HomeView';
import CourseView from './pages/CourseView';
import './index.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomeView />} />
        <Route path="/course/:id" element={<CourseView />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
