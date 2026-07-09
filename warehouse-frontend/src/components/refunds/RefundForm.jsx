import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Typography,
  Card,
  CardContent,
  IconButton,
  Switch,
  FormControlLabel,
  CircularProgress,
} from '@mui/material';
import { Delete as DeleteIcon, Add as AddIcon } from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { saleApi, refundApi } from '../../services/api';
import toast from 'react-hot-toast';

const RefundForm = ({ onSuccess }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [sales, setSales] = useState([]);
  const [saleItems, setSaleItems] = useState([]);
  const [formData, setFormData] = useState({
    sale_id: '',
    employee_id: user?.id || '',
    reason: '',
    restock_items: true,
    items: [{ sale_item_id: '', quantity: 1, refund_unit_price: '', restock: true }],
  });

  useEffect(() => {
    fetchSales();
  }, []);

  const fetchSales = async () => {
    try {
      const response = await saleApi.getAll();
      // Filter sales that have not been fully refunded (we'll handle server-side validation)
      setSales(response.data);
    } catch (error) {
      toast.error('Failed to load sales');
    }
  };

  const fetchSaleItems = async (saleId) => {
    try {
      const response = await saleApi.getById(saleId);
      setSaleItems(response.data.items);
    } catch (error) {
      toast.error('Failed to load sale items');
    }
  };

  const handleSaleChange = (saleId) => {
    setFormData({ ...formData, sale_id: saleId, items: [{ sale_item_id: '', quantity: 1, refund_unit_price: '', restock: true }] });
    if (saleId) {
      fetchSaleItems(saleId);
    } else {
      setSaleItems([]);
    }
  };

  const handleItemChange = (index, field, value) => {
    const updatedItems = [...formData.items];
    updatedItems[index][field] = value;
    setFormData({ ...formData, items: updatedItems });
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { sale_item_id: '', quantity: 1, refund_unit_price: '', restock: true }],
    });
  };

  const removeItem = (index) => {
    const updatedItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: updatedItems });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Validate items
      for (const item of formData.items) {
        if (!item.sale_item_id || item.quantity < 1) {
          toast.error('Please fill in all item fields correctly');
          setLoading(false);
          return;
        }
      }
      // Convert employee_id to number
      const payload = {
        ...formData,
        employee_id: parseInt(formData.employee_id),
        sale_id: parseInt(formData.sale_id),
        items: formData.items.map(item => ({
          ...item,
          sale_item_id: parseInt(item.sale_item_id),
          quantity: parseInt(item.quantity),
          refund_unit_price: item.refund_unit_price ? parseFloat(item.refund_unit_price) : undefined,
          restock: item.restock,
        })),
      };
      await refundApi.create(payload);
      toast.success('Refund processed successfully!');
      if (onSuccess) onSuccess();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to process refund');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Sale</InputLabel>
              <Select
                value={formData.sale_id}
                onChange={(e) => handleSaleChange(e.target.value)}
                required
              >
                {sales.map((sale) => (
                  <MenuItem key={sale.id} value={sale.id}>
                    #{sale.id} - {sale.employee_name} - ${sale.total_amount}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Reason"
              name="reason"
              value={formData.reason}
              onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
            />
          </Grid>
          <Grid item xs={12}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.restock_items}
                  onChange={(e) => setFormData({ ...formData, restock_items: e.target.checked })}
                />
              }
              label="Restock items by default"
            />
          </Grid>

          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Refund Items
            </Typography>
            {formData.items.map((item, index) => (
              <Card key={index} sx={{ mb: 2 }}>
                <CardContent>
                  <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} md={4}>
                      <FormControl fullWidth>
                        <InputLabel>Sale Item</InputLabel>
                        <Select
                          value={item.sale_item_id}
                          onChange={(e) => handleItemChange(index, 'sale_item_id', e.target.value)}
                          required
                        >
                          {saleItems.map((si) => (
                            <MenuItem key={si.id} value={si.id}>
                              {si.product_name} (Qty: {si.quantity}) - ${si.unit_selling_price}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={6} md={2}>
                      <TextField
                        fullWidth
                        label="Quantity"
                        type="number"
                        value={item.quantity}
                        onChange={(e) => handleItemChange(index, 'quantity', parseInt(e.target.value) || 0)}
                        required
                        inputProps={{ min: 1 }}
                      />
                    </Grid>
                    <Grid item xs={6} md={2}>
                      <TextField
                        fullWidth
                        label="Unit Price"
                        type="number"
                        value={item.refund_unit_price}
                        onChange={(e) => handleItemChange(index, 'refund_unit_price', parseFloat(e.target.value) || '')}
                        placeholder="Original price"
                        inputProps={{ step: '0.01' }}
                      />
                    </Grid>
                    <Grid item xs={6} md={2}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={item.restock}
                            onChange={(e) => handleItemChange(index, 'restock', e.target.checked)}
                          />
                        }
                        label="Restock"
                      />
                    </Grid>
                    <Grid item xs={6} md={2}>
                      <IconButton
                        color="error"
                        onClick={() => removeItem(index)}
                        disabled={formData.items.length === 1}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ))}
            <Button
              variant="outlined"
              startIcon={<AddIcon />}
              onClick={addItem}
            >
              Add Item
            </Button>
          </Grid>

          <Grid item xs={12}>
            <Box display="flex" gap={2} justifyContent="flex-end">
              <Button
                type="submit"
                variant="contained"
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Process Refund'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Box>
  );
};

export default RefundForm;