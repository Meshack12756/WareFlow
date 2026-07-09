import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  MenuItem,
} from '@mui/material';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'worker',
    pay_model: 'A',
    hourly_rate: 0,
    commission_rate: 0,
    bonus_rate: 0,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    const success = await register(formData);
    setLoading(false);
    
    if (success) {
      navigate('/login');
    } else {
      setError('Registration failed. Please try again.');
    }
  };

  return (
    <Container component="main" maxWidth="sm">
      <Box sx={{ marginTop: 4, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          <Typography component="h1" variant="h5" align="center">
            Register
          </Typography>
          
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
          
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              name="name"
              label="Full Name"
              value={formData.name}
              onChange={handleChange}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="email"
              label="Email Address"
              type="email"
              value={formData.email}
              onChange={handleChange}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              value={formData.password}
              onChange={handleChange}
            />
            <TextField
              margin="normal"
              fullWidth
              select
              name="role"
              label="Role"
              value={formData.role}
              onChange={handleChange}
            >
              <MenuItem value="admin">Admin</MenuItem>
              <MenuItem value="worker">Worker</MenuItem>
            </TextField>
            <TextField
              margin="normal"
              fullWidth
              select
              name="pay_model"
              label="Pay Model"
              value={formData.pay_model}
              onChange={handleChange}
            >
              <MenuItem value="A">Model A - Commission</MenuItem>
              <MenuItem value="B">Model B - Hourly + Bonus</MenuItem>
              <MenuItem value="C">Model C - Profit Share</MenuItem>
            </TextField>
            <TextField
              margin="normal"
              fullWidth
              name="hourly_rate"
              label="Hourly Rate (Model B)"
              type="number"
              value={formData.hourly_rate}
              onChange={handleChange}
            />
            <TextField
              margin="normal"
              fullWidth
              name="commission_rate"
              label="Commission Rate % (Model A)"
              type="number"
              value={formData.commission_rate}
              onChange={handleChange}
            />
            <TextField
              margin="normal"
              fullWidth
              name="bonus_rate"
              label="Bonus Rate % (Model B)"
              type="number"
              value={formData.bonus_rate}
              onChange={handleChange}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Registering...' : 'Register'}
            </Button>
            <Box sx={{ textAlign: 'center' }}>
              <Link to="/login" style={{ textDecoration: 'none' }}>
                <Typography variant="body2" color="primary">
                  Already have an account? Login
                </Typography>
              </Link>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
};

export default Register;