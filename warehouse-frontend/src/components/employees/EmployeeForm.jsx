import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../services/api';
import toast from 'react-hot-toast';

const EmployeeForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
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

  useEffect(() => {
    if (id) {
      fetchEmployee();
    }
  }, [id]);

  const fetchEmployee = async () => {
    try {
      const response = await api.get(`/employees/${id}`);
      setFormData(response.data);
    } catch (error) {
      toast.error('Failed to load employee');
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (id) {
        await api.put(`/employees/${id}`, formData);
        toast.success('Employee updated successfully');
      } else {
        await api.post('/employees', formData);
        toast.success('Employee created successfully');
      }
      navigate('/employees');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save employee');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        {id ? 'Edit Employee' : 'Add Employee'}
      </Typography>

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </Grid>
            {!id && (
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                />
              </Grid>
            )}
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Role</InputLabel>
                <Select
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                >
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="worker">Worker</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Pay Model</InputLabel>
                <Select
                  name="pay_model"
                  value={formData.pay_model}
                  onChange={handleChange}
                >
                  <MenuItem value="A">Model A - Commission</MenuItem>
                  <MenuItem value="B">Model B - Hourly + Bonus</MenuItem>
                  <MenuItem value="C">Model C - Profit Share</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Hourly Rate"
                name="hourly_rate"
                type="number"
                value={formData.hourly_rate}
                onChange={handleChange}
                inputProps={{ step: '0.01' }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Commission Rate (%)"
                name="commission_rate"
                type="number"
                value={formData.commission_rate}
                onChange={handleChange}
                inputProps={{ step: '0.01' }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Bonus Rate (%)"
                name="bonus_rate"
                type="number"
                value={formData.bonus_rate}
                onChange={handleChange}
                inputProps={{ step: '0.01' }}
              />
            </Grid>
            <Grid item xs={12}>
              <Box display="flex" gap={2}>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                >
                  {loading ? 'Saving...' : 'Save'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => navigate('/employees')}
                >
                  Cancel
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Box>
  );
};

export default EmployeeForm;