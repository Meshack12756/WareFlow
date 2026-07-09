import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Typography,
  Box,
  Chip,
  IconButton,
} from '@mui/material';
import { Add as AddIcon, Visibility as ViewIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { format } from 'date-fns';

const SalesList = () => {
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchSales();
  }, []);

  const fetchSales = async () => {
    try {
      const response = await api.get('/sales');
      setSales(response.data);
    } catch (error) {
      console.error('Failed to load sales:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <Typography>Loading sales...</Typography>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Sales</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => navigate('/sales/new')}
        >
          New Sale
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Sale ID</TableCell>
              <TableCell>Employee</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Items</TableCell>
              <TableCell>Total Amount</TableCell>
              <TableCell>Profit</TableCell>
              <TableCell>Actions</TableCell>
              <TableCell>Refunded</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sales.map((sale) => (
              <TableRow key={sale.id}>
                <TableCell>#{sale.id}</TableCell>
                <TableCell>{sale.employee_name}</TableCell>
                <TableCell>{format(new Date(sale.timestamp), 'MMM d, yyyy HH:mm')}</TableCell>
                <TableCell>{sale.items?.length || 0}</TableCell>
                <TableCell>${sale.total_amount}</TableCell>
                <TableCell>
                  {sale.refunded_amount ? `$${sale.refunded_amount}` : '—'}
                </TableCell>
                <TableCell>
                  <Chip
                    label={`$${sale.gross_profit}`}
                    color={sale.gross_profit > 0 ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => navigate(`/sales/${sale.id}`)}
                    color="primary"
                    size="small"
                  >
                    <ViewIcon />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default SalesList;