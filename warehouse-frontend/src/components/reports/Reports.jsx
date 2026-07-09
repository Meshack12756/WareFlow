// src/components/reports/Reports.jsx
import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import api from '../../services/api';
import { useAuth } from '../../context/AuthContext';

// Color palette for charts
const COLORS = ['#1a237e', '#0d47a1', '#00bcd4', '#2e7d32', '#ed6c02', '#d32f2f', '#6a1b9a', '#00695c'];
const COLORS_LOW_STOCK = ['#d32f2f', '#ed6c02', '#f57c00'];

const Reports = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [topProducts, setTopProducts] = useState([]);
  const [lowStock, setLowStock] = useState([]);
  const [employeePerformance, setEmployeePerformance] = useState([]);
  const [dailySales, setDailySales] = useState([]);

  useEffect(() => {
    fetchReports();
  }, []);

  const fetchReports = async () => {
    try {
      const [productsRes, stockRes, performanceRes, dailyRes] = await Promise.all([
        api.get('/reports/sales/top-products?days=30&limit=5'),
        api.get('/reports/inventory/low-stock?threshold=10'),
        api.get('/reports/employee/performance?days=30'),
        api.get('/reports/sales/daily?days=7'),
      ]);

      setTopProducts(productsRes.data);
      setLowStock(stockRes.data);
      setEmployeePerformance(performanceRes.data);
      setDailySales(dailyRes.data);
    } catch (error) {
      console.error('Failed to load reports:', error);
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

  // Prepare data for charts
  const topProductsChartData = topProducts.map((item) => ({
    name: item.name.length > 15 ? item.name.substring(0, 12) + '...' : item.name,
    Revenue: item.total_revenue,
    Quantity: item.total_quantity,
    fullName: item.name,
  }));

  const lowStockChartData = lowStock.map((item) => ({
    name: item.name.length > 15 ? item.name.substring(0, 12) + '...' : item.name,
    Stock: item.stock_quantity,
    fullName: item.name,
  }));

  const employeeChartData = employeePerformance.map((item) => ({
    name: item.name.length > 15 ? item.name.substring(0, 12) + '...' : item.name,
    Sales: item.sales_count,
    Profit: item.total_profit,
    Revenue: item.total_revenue,
    fullName: item.name,
  }));

  const dailySalesChartData = dailySales.map((item) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    Revenue: item.total_revenue,
    Profit: item.total_profit,
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reports & Analytics
      </Typography>

      <Grid container spacing={3}>
        {/* Top Products - Bar Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top Selling Products
              </Typography>
              {topProducts.length === 0 ? (
                <Typography color="textSecondary">No data available</Typography>
              ) : (
                <Box sx={{ width: '100%', height: 280 }}>
                  <ResponsiveContainer>
                    <BarChart data={topProductsChartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis dataKey="name" stroke="#888" />
                      <YAxis stroke="#888" />
                      <Tooltip
                        contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                        formatter={(value, name) => {
                          if (name === 'Revenue') return [`$${value.toFixed(2)}`, name];
                          return [value, name];
                        }}
                        labelFormatter={(label, items) => {
                          const item = items[0]?.payload;
                          return item?.fullName || label;
                        }}
                      />
                      <Legend />
                      <Bar dataKey="Revenue" fill="#1a237e" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Quantity" fill="#00bcd4" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              )}
              {/* Table summary below chart */}
              <TableContainer component={Paper} elevation={0} sx={{ mt: 2 }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Product</TableCell>
                      <TableCell align="right">Quantity</TableCell>
                      <TableCell align="right">Revenue</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {topProducts.map((product) => (
                      <TableRow key={product.id}>
                        <TableCell>{product.name}</TableCell>
                        <TableCell align="right">{product.total_quantity}</TableCell>
                        <TableCell align="right">${product.total_revenue.toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Low Stock Items - Bar Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Low Stock Items
              </Typography>
              {lowStock.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4 }}>
                  <Typography color="success.main" variant="h6">
                    ✅ All items are well stocked!
                  </Typography>
                </Box>
              ) : (
                <>
                  <Box sx={{ width: '100%', height: 200 }}>
                    <ResponsiveContainer>
                      <BarChart data={lowStockChartData} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis type="number" stroke="#888" />
                        <YAxis dataKey="name" type="category" stroke="#888" width={80} />
                        <Tooltip
                          contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                          labelFormatter={(label, items) => {
                            const item = items[0]?.payload;
                            return item?.fullName || label;
                          }}
                        />
                        <Bar dataKey="Stock" radius={[0, 4, 4, 0]}>
                          {lowStockChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.Stock < 5 ? '#d32f2f' : '#ed6c02'} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                  <TableContainer component={Paper} elevation={0} sx={{ mt: 2 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Product</TableCell>
                          <TableCell align="right">Stock</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {lowStock.map((product) => (
                          <TableRow key={product.id}>
                            <TableCell>{product.name}</TableCell>
                            <TableCell align="right">
                              <Chip
                                label={product.stock_quantity}
                                color={product.stock_quantity < 5 ? 'error' : 'warning'}
                                size="small"
                              />
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Employee Performance - Bar Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Employee Performance (Last 30 Days)
              </Typography>
              {employeePerformance.length === 0 ? (
                <Typography color="textSecondary">No data available</Typography>
              ) : (
                <>
                  <Box sx={{ width: '100%', height: 280 }}>
                    <ResponsiveContainer>
                      <BarChart data={employeeChartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="name" stroke="#888" />
                        <YAxis stroke="#888" />
                        <Tooltip
                          contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                          formatter={(value, name) => {
                            if (name === 'Revenue' || name === 'Profit') return [`$${value.toFixed(2)}`, name];
                            return [value, name];
                          }}
                          labelFormatter={(label, items) => {
                            const item = items[0]?.payload;
                            return item?.fullName || label;
                          }}
                        />
                        <Legend />
                        <Bar dataKey="Sales" fill="#0d47a1" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Revenue" fill="#00bcd4" radius={[4, 4, 0, 0]} />
                        <Bar dataKey="Profit" fill="#2e7d32" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </Box>
                  <TableContainer component={Paper} elevation={0} sx={{ mt: 2 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Employee</TableCell>
                          <TableCell align="right">Sales</TableCell>
                          <TableCell align="right">Revenue</TableCell>
                          <TableCell align="right">Profit</TableCell>
                          <TableCell align="right">Avg / Sale</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {employeePerformance.map((emp) => (
                          <TableRow key={emp.id}>
                            <TableCell>{emp.name}</TableCell>
                            <TableCell align="right">{emp.sales_count}</TableCell>
                            <TableCell align="right">${emp.total_revenue.toFixed(2)}</TableCell>
                            <TableCell align="right">${emp.total_profit.toFixed(2)}</TableCell>
                            <TableCell align="right">${emp.avg_profit_per_sale.toFixed(2)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Daily Sales Trend - Line Chart */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Daily Sales Trend (Last 7 Days)
              </Typography>
              {dailySales.length === 0 ? (
                <Typography color="textSecondary">No data available</Typography>
              ) : (
                <>
                  <Box sx={{ width: '100%', height: 280 }}>
                    <ResponsiveContainer>
                      <LineChart data={dailySalesChartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                        <XAxis dataKey="date" stroke="#888" />
                        <YAxis stroke="#888" />
                        <Tooltip
                          contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                          formatter={(value) => [`$${value.toFixed(2)}`, '']}
                        />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="Revenue"
                          stroke="#1a237e"
                          strokeWidth={3}
                          dot={{ r: 5, fill: '#1a237e' }}
                          activeDot={{ r: 7 }}
                        />
                        <Line
                          type="monotone"
                          dataKey="Profit"
                          stroke="#2e7d32"
                          strokeWidth={3}
                          dot={{ r: 5, fill: '#2e7d32' }}
                          activeDot={{ r: 7 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                  <TableContainer component={Paper} elevation={0} sx={{ mt: 2 }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Date</TableCell>
                          <TableCell align="right">Sales</TableCell>
                          <TableCell align="right">Revenue</TableCell>
                          <TableCell align="right">Profit</TableCell>
                          <TableCell align="right">Avg / Sale</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {dailySales.map((day) => (
                          <TableRow key={day.date}>
                            <TableCell>{new Date(day.date).toLocaleDateString()}</TableCell>
                            <TableCell align="right">{day.sales_count}</TableCell>
                            <TableCell align="right">${day.total_revenue.toFixed(2)}</TableCell>
                            <TableCell align="right">${day.total_profit.toFixed(2)}</TableCell>
                            <TableCell align="right">
                              ${day.sales_count > 0 ? (day.total_revenue / day.sales_count).toFixed(2) : '0.00'}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Reports;