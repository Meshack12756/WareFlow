import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import AnimatedCard from '../Animations/AnimatedCard';
import SalesTrendChart from './SalesTrendChart';
import api from '../../services/api';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Button,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  ShoppingCart as SalesIcon,
  AttachMoney as RevenueIcon,
  AccountBalance as ProfitIcon,
  Inventory as InventoryIcon,
} from "@mui/icons-material";

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalSales: 0,
    totalRevenue: 0,
    totalProfit: 0,
    lowStock: 0,
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [todaySummary, lowStock] = await Promise.all([
        api.get('/sales/summary/today'),
        api.get('/reports/inventory/low-stock?threshold=10'),
      ]);

      setStats({
        totalSales: todaySummary.data.total_sales || 0,
        totalRevenue: todaySummary.data.net_revenue || 0,
        totalProfit: todaySummary.data.net_profit || 0,
        lowStock: lowStock.data.length || 0,
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const cards = [
    {
      title: "Today's Sales",
      value: stats.totalSales,
      icon: <SalesIcon sx={{ fontSize: 40 }} />,
      color: '#1976d2',
    },
    {
      title: "Revenue",
      value: `$${stats.totalRevenue.toFixed(2)}`,
      icon: <RevenueIcon sx={{ fontSize: 40 }} />,
      color: '#2e7d32',
    },
    {
      title: "Profit",
      value: `$${stats.totalProfit.toFixed(2)}`,
      icon: <ProfitIcon sx={{ fontSize: 40 }} />,
      color: '#ed6c02',
    },
    {
      title: "Low Stock Items",
      value: stats.lowStock,
      icon: <InventoryIcon sx={{ fontSize: 40 }} />,
      color: '#d32f2f',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.name}!
      </Typography>
      <Typography variant="body1" color="textSecondary" gutterBottom>
        {user?.role === 'admin' ? 'Admin Dashboard' : 'Worker Dashboard'}
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {cards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <AnimatedCard
              title={card.title}
              value={card.value}
              icon={card.icon}
              color={card.color}
              delay={index * 0.1}
            />
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="contained"
                  color="primary"
                  onClick={() => navigate('/sales/new')}
                >
                  New Sale
                </Button>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="contained"
                  color="secondary"
                  onClick={() => navigate('/products')}
                >
                  Manage Products
                </Button>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Button
                  fullWidth
                  variant="contained"
                  color="success"
                  onClick={() => navigate('/reports')}
                >
                  View Reports
                </Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </Box>

      <Box sx={{ mt: 4 }}>
        <SalesTrendChart />
      </Box>
    </Box>
  );
};

export default Dashboard;