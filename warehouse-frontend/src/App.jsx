import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';

// Layout
import Layout from './components/Layout';

// Auth Pages
import Login from './components/auth/Login';
import Register from './components/auth/Register';

// Dashboard
import Dashboard from './components/dashboard/Dashboard';

// Products
import ProductList from './components/products/ProductList';
import ProductForm from './components/products/ProductForm';

// Sales
import SalesList from './components/sales/SalesList';
import SalesForm from './components/sales/SalesForm';

// Employees
import EmployeeList from './components/employees/EmployeeList';
import EmployeeForm from './components/employees/EmployeeForm';

// Reports
import Reports from './components/reports/Reports';

// Page Transition
import PageTransition from './components/Animations/PageTransition';

const PrivateRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex justify-center items-center h-screen">Loading...</div>;
  return user ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Toaster position="top-right" />
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/*"
              element={
                <PrivateRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<PageTransition><Dashboard /></PageTransition>} />
                      <Route path="/products" element={<PageTransition><ProductList /></PageTransition>} />
                      <Route path="/products/new" element={<PageTransition><ProductForm /></PageTransition>} />
                      <Route path="/products/edit/:id" element={<PageTransition><ProductForm /></PageTransition>} />
                      <Route path="/sales" element={<PageTransition><SalesList /></PageTransition>} />
                      <Route path="/sales/new" element={<PageTransition><SalesForm /></PageTransition>} />
                      <Route path="/employees" element={<PageTransition><EmployeeList /></PageTransition>} />
                      <Route path="/employees/new" element={<PageTransition><EmployeeForm /></PageTransition>} />
                      <Route path="/employees/edit/:id" element={<PageTransition><EmployeeForm /></PageTransition>} />
                      <Route path="/reports" element={<PageTransition><Reports /></PageTransition>} />
                    </Routes>
                  </Layout>
                </PrivateRoute>
              }
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export const refundApi = {
  create: (data) => api.post('/refunds/', data),
  getAll: (params) => api.get('/refunds/', { params }),
  getById: (id) => api.get(`/refunds/${id}`),
  getBySale: (saleId) => api.get(`/refunds/sale/${saleId}`),
};

export default App;