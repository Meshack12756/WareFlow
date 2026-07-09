import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  Chip,
  IconButton,
  Button,
  TextField,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { Visibility as ViewIcon, Receipt as ReceiptIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import { refundApi } from '../../services/api';
import toast from 'react-hot-toast';
import RefundForm from './RefundForm';

const RefundList = () => {
  const [refunds, setRefunds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ sale_id: '', employee_id: '' });
  const [openForm, setOpenForm] = useState(false);
  const [selectedRefund, setSelectedRefund] = useState(null);

  useEffect(() => {
    fetchRefunds();
  }, []);

  const fetchRefunds = async () => {
    try {
      const params = {};
      if (filters.sale_id) params.sale_id = filters.sale_id;
      if (filters.employee_id) params.employee_id = filters.employee_id;
      const response = await refundApi.getAll(params);
      setRefunds(response.data);
    } catch (error) {
      toast.error('Failed to load refunds');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const applyFilters = () => {
    fetchRefunds();
  };

  const handleViewDetails = (refund) => {
    setSelectedRefund(refund);
    // You can open a dialog or navigate to details page
  };

  if (loading) return <Typography>Loading refunds...</Typography>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Refunds</Typography>
        <Button
          variant="contained"
          startIcon={<ReceiptIcon />}
          onClick={() => setOpenForm(true)}
        >
          New Refund
        </Button>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Sale ID"
              name="sale_id"
              value={filters.sale_id}
              onChange={handleFilterChange}
              type="number"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Employee ID"
              name="employee_id"
              value={filters.employee_id}
              onChange={handleFilterChange}
              type="number"
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <Button variant="outlined" onClick={applyFilters} fullWidth>
              Apply Filters
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Refunds Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Refund ID</TableCell>
              <TableCell>Sale ID</TableCell>
              <TableCell>Employee</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Items</TableCell>
              <TableCell>Amount</TableCell>
              <TableCell>Restock</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {refunds.map((refund) => (
              <TableRow key={refund.id}>
                <TableCell>#{refund.id}</TableCell>
                <TableCell>#{refund.sale_id}</TableCell>
                <TableCell>{refund.employee_name}</TableCell>
                <TableCell>{format(new Date(refund.refund_date), 'MMM d, yyyy HH:mm')}</TableCell>
                <TableCell>{refund.items?.length || 0}</TableCell>
                <TableCell>${refund.total_refund_amount}</TableCell>
                <TableCell>
                  <Chip
                    label={refund.restock_items ? 'Restock' : 'No Restock'}
                    color={refund.restock_items ? 'success' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => handleViewDetails(refund)}
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

      {/* Create Refund Dialog */}
      <Dialog open={openForm} onClose={() => setOpenForm(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create Refund</DialogTitle>
        <DialogContent>
          <RefundForm onSuccess={() => { setOpenForm(false); fetchRefunds(); }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenForm(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RefundList;