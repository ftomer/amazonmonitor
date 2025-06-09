import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  Plus, 
  Edit3, 
  Trash2, 
  DollarSign, 
  Settings, 
  Activity,
  RefreshCw,
  Mail,
  Bell,
  ExternalLink,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

// Use environment variable or fallback for API base URL
const API_BASE = process.env.REACT_APP_API_URL || '/api';

const PriceMonitorApp = () => {
  const [status, setStatus] = useState({ is_running: false, total_products: 0 });
  const [products, setProducts] = useState([]);
  const [config, setConfig] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(false);
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [priceHistory, setPriceHistory] = useState({});
  const [logs, setLogs] = useState([]);
  const [lastCheck, setLastCheck] = useState([]);
  const [error, setError] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('checking');

  // API helper with error handling
  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API call failed for ${endpoint}:`, error);
      setError(`Failed to ${endpoint.split('/').pop()}: ${error.message}`);
      throw error;
    }
  };

  // Fetch data functions with error handling
  const fetchStatus = async () => {
    try {
      const data = await apiCall('/status');
      setStatus(data);
      setConnectionStatus('connected');
      setError(null);
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const fetchProducts = async () => {
    try {
      const data = await apiCall('/products');
      setProducts(data);
    } catch (error) {
      // Handle error silently if already displayed
    }
  };

  const fetchConfig = async () => {
    try {
      const data = await apiCall('/config');
      setConfig(data);
    } catch (error) {
      // Handle error silently if already displayed
    }
  };

  const fetchPriceHistory = async () => {
    try {
      const data = await apiCall('/price-history');
      setPriceHistory(data);
    } catch (error) {
      // Handle error silently
    }
  };

  const fetchLogs = async () => {
    try {
      const data = await apiCall('/logs?lines=50');
      setLogs(data.logs || []);
    } catch (error) {
      // Handle error silently
    }
  };

  // Control functions
  const toggleMonitoring = async () => {
    setLoading(true);
    try {
      const endpoint = status.is_running ? '/monitor/stop' : '/monitor/start';
      await apiCall(endpoint, { method: 'POST' });
      await fetchStatus();
      setError(null);
    } catch (error) {
      // Error already handled by apiCall
    }
    setLoading(false);
  };

  const checkPricesNow = async () => {
    setLoading(true);
    try {
      const data = await apiCall('/check-now', { method: 'POST' });
      setLastCheck(data.results);
      await fetchPriceHistory();
      setError(null);
    } catch (error) {
      // Error already handled by apiCall
    }
    setLoading(false);
  };

  const addProduct = async (product) => {
    try {
      await apiCall('/products', {
        method: 'POST',
        body: JSON.stringify(product)
      });
      
      await fetchProducts();
      await fetchStatus();
      setShowAddProduct(false);
      setError(null);
    } catch (error) {
      // Error already handled by apiCall
    }
  };

  const updateProduct = async (index, updates) => {
    try {
      await apiCall(`/products/${index}`, {
        method: 'PUT',
        body: JSON.stringify(updates)
      });
      
      await fetchProducts();
      setEditingProduct(null);
      setError(null);
    } catch (error) {
      // Error already handled by apiCall
    }
  };

  const deleteProduct = async (index) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await apiCall(`/products/${index}`, { method: 'DELETE' });
        await fetchProducts();
        await fetchStatus();
        setError(null);
      } catch (error) {
        // Error already handled by apiCall
      }
    }
  };

  // Load data on component mount
  useEffect(() => {
    fetchStatus();
    fetchProducts();
    fetchConfig();
    fetchPriceHistory();
    
    // Refresh data every 30 seconds
    const interval = setInterval(() => {
      fetchStatus();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Connection Status Component
  const ConnectionStatus = () => (
    <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${
      connectionStatus === 'connected' 
        ? 'bg-green-100 text-green-800' 
        : connectionStatus === 'disconnected'
        ? 'bg-red-100 text-red-800'
        : 'bg-yellow-100 text-yellow-800'
    }`}>
      <div className={`w-2 h-2 rounded-full mr-2 ${
        connectionStatus === 'connected' 
          ? 'bg-green-400' 
          : connectionStatus === 'disconnected'
          ? 'bg-red-400'
          : 'bg-yellow-400'
      }`} />
      {connectionStatus === 'connected' ? 'API Connected' : 
       connectionStatus === 'disconnected' ? 'API Disconnected' : 'Connecting...'}
    </div>
  );

  // Error Alert Component
  const ErrorAlert = () => error && (
    <div className="mb-4 p-4 bg-red-100 border border-red-300 rounded-md">
      <div className="flex items-center">
        <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
        <span className="text-red-800">{error}</span>
        <button 
          onClick={() => setError(null)}
          className="ml-auto text-red-500 hover:text-red-700"
        >
          ×
        </button>
      </div>
    </div>
  );

  // Mock data for development when API is not available
  const mockData = connectionStatus === 'disconnected' ? {
    status: { is_running: false, total_products: 2 },
    products: [
      {
        name: "Echo Dot (3rd Gen) - Mock Data",
        url: "https://www.amazon.com/gp/product/B0757911C2/",
        target_price: 30.00
      },
      {
        name: "iPad Air - Mock Data", 
        url: "https://www.amazon.com/gp/product/B09G9FPHY6/",
        target_price: 500.00
      }
    ],
    config: {
      check_interval_minutes: 60,
      email_notifications: { email_enabled: false, desktop_enabled: true }
    }
  } : { status, products, config };

  // Components (keeping the same components from before)
  const ProductCard = ({ product, index }) => (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-800 truncate flex-1 mr-4">
          {product.name}
        </h3>
        <div className="flex space-x-2">
          <button
            onClick={() => setEditingProduct({ ...product, index })}
            className="p-1 text-gray-400 hover:text-blue-600 transition-colors"
            disabled={connectionStatus === 'disconnected'}
          >
            <Edit3 size={16} />
          </button>
          <button
            onClick={() => deleteProduct(index)}
            className="p-1 text-gray-400 hover:text-red-600 transition-colors"
            disabled={connectionStatus === 'disconnected'}
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Target Price:</span>
          <span className="text-lg font-bold text-green-600">
            ${product.target_price.toFixed(2)}
          </span>
        </div>
        
        {lastCheck.find && lastCheck.find(check => check.name === product.name) && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Current Price:</span>
            <span className="text-lg font-bold text-blue-600">
              ${lastCheck.find(check => check.name === product.name)?.current_price?.toFixed(2) || 'N/A'}
            </span>
          </div>
        )}
        
        <a
          href={product.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
        >
          View on Amazon <ExternalLink size={14} className="ml-1" />
        </a>
      </div>
    </div>
  );

  const AddProductForm = () => {
    const [formData, setFormData] = useState({
      name: '',
      url: '',
      target_price: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      addProduct({
        name: formData.name,
        url: formData.url,
        target_price: parseFloat(formData.target_price)
      });
    };

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-md">
          <h3 className="text-lg font-semibold mb-4">Add New Product</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Name
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                placeholder="Echo Dot (3rd Gen)"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Amazon URL
              </label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://www.amazon.com/..."
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Price ($)
              </label>
              <input
                type="number"
                step="0.01"
                min="0"
                value={formData.target_price}
                onChange={(e) => setFormData({ ...formData, target_price: e.target.value })}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="29.99"
                required
              />
            </div>
            <div className="flex space-x-3">
              <button
                type="submit"
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                disabled={connectionStatus === 'disconnected'}
              >
                Add Product
              </button>
              <button
                type="button"
                onClick={() => setShowAddProduct(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  const Dashboard = () => (
    <div className="space-y-6">
      <ErrorAlert />
      
      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center">
            <Activity className={`h-8 w-8 ${mockData.status.is_running ? 'text-green-500' : 'text-red-500'}`} />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Status</p>
              <p className="text-lg font-semibold">
                {mockData.status.is_running ? 'Running' : 'Stopped'}
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Products</p>
              <p className="text-lg font-semibold">{mockData.status.total_products}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Interval</p>
              <p className="text-lg font-semibold">
                {mockData.config?.check_interval_minutes || 60}m
              </p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <div className="flex items-center">
            <Bell className="h-8 w-8 text-yellow-500" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Notifications</p>
              <p className="text-lg font-semibold">
                {mockData.config?.email_notifications?.email_enabled ? 'Email' : 'Desktop'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h3 className="text-lg font-semibold mb-4">Controls</h3>
        <div className="flex space-x-4">
          <button
            onClick={toggleMonitoring}
            disabled={loading || connectionStatus === 'disconnected'}
            className={`flex items-center px-4 py-2 rounded-md font-medium transition-colors ${
              mockData.status.is_running
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-green-600 hover:bg-green-700 text-white'
            } ${(loading || connectionStatus === 'disconnected') ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {mockData.status.is_running ? <Pause className="mr-2" size={18} /> : <Play className="mr-2" size={18} />}
            {mockData.status.is_running ? 'Stop Monitoring' : 'Start Monitoring'}
          </button>
          
          <button
            onClick={checkPricesNow}
            disabled={loading || connectionStatus === 'disconnected'}
            className={`flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors ${
              (loading || connectionStatus === 'disconnected') ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            <RefreshCw className={`mr-2 ${loading ? 'animate-spin' : ''}`} size={18} />
            Check Prices Now
          </button>
        </div>
        
        {connectionStatus === 'disconnected' && (
          <div className="mt-4 p-3 bg-yellow-100 rounded-md">
            <p className="text-sm text-yellow-800">
              <strong>Development Mode:</strong> API not available. UI functionality is limited to visual testing.
            </p>
          </div>
        )}
      </div>

      {/* Recent Check Results */}
      {lastCheck.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
          <h3 className="text-lg font-semibold mb-4">Last Price Check</h3>
          <div className="space-y-3">
            {lastCheck.map((result, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <span className="font-medium">{result.name}</span>
                <div className="flex items-center space-x-4">
                  {result.error ? (
                    <span className="text-red-600 text-sm">Error: {result.error}</span>
                  ) : (
                    <>
                      <span className="text-lg font-bold">
                        ${result.current_price?.toFixed(2) || 'N/A'}
                      </span>
                      {result.price_met ? (
                        <CheckCircle className="text-green-500" size={20} />
                      ) : (
                        <XCircle className="text-gray-400" size={20} />
                      )}
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const ProductsTab = () => (
    <div className="space-y-6">
      <ErrorAlert />
      
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Products</h2>
        <button
          onClick={() => setShowAddProduct(true)}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors"
          disabled={connectionStatus === 'disconnected'}
        >
          <Plus className="mr-2" size={18} />
          Add Product
        </button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {mockData.products.map((product, index) => (
          <ProductCard key={index} product={product} index={index} />
        ))}
      </div>
      
      {mockData.products.length === 0 && (
        <div className="text-center py-12">
          <DollarSign className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No products</h3>
          <p className="mt-1 text-sm text-gray-500">
            Add your first product to start monitoring Amazon prices.
          </p>
        </div>
      )}
    </div>
  );

  const LogsTab = () => (
    <div className="space-y-6">
      <ErrorAlert />
      
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-800">Logs</h2>
        <button
          onClick={fetchLogs}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md font-medium transition-colors"
          disabled={connectionStatus === 'disconnected'}
        >
          <RefreshCw className="mr-2" size={18} />
          Refresh Logs
        </button>
      </div>
      
      <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm h-96 overflow-y-auto">
        {logs.length > 0 ? (
          logs.map((log, index) => (
            <div key={index} className="mb-1">
              {log.trim()}
            </div>
          ))
        ) : connectionStatus === 'disconnected' ? (
          <div className="text-gray-500">
            Mock logs would appear here when API is connected...
            <br />
            2024-06-09 10:30:15 - INFO - Amazon Price Monitor started
            <br />
            2024-06-09 10:30:16 - INFO - Checking price for Echo Dot
            <br />
            2024-06-09 10:30:18 - INFO - Current price $29.99, Target: $30.00
            <br />
            2024-06-09 10:30:18 - INFO - Price alert triggered!
          </div>
        ) : (
          <div className="text-gray-500">No logs available</div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <TrendingDown className="h-8 w-8 text-blue-600 mr-3" />
              <h1 className="text-xl font-bold text-gray-900">
                Amazon Price Monitor
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <ConnectionStatus />
              <div className={`flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                mockData.status.is_running 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                <div className={`w-2 h-2 rounded-full mr-2 ${
                  mockData.status.is_running ? 'bg-green-400' : 'bg-red-400'
                }`} />
                {mockData.status.is_running ? 'Active' : 'Inactive'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: Activity },
              { id: 'products', label: 'Products', icon: DollarSign },
              { id: 'logs', label: 'Logs', icon: Settings }
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id)}
                className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="mr-2" size={16} />
                {label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'products' && <ProductsTab />}
        {activeTab === 'logs' && <LogsTab />}
      </main>

      {/* Modals */}
      {showAddProduct && <AddProductForm />}
      
      {editingProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Edit Product</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              updateProduct(editingProduct.index, {
                name: formData.get('name'),
                url: formData.get('url'),
                target_price: parseFloat(formData.get('target_price'))
              });
            }} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product Name
                </label>
                <input
                  type="text"
                  name="name"
                  defaultValue={editingProduct.name}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amazon URL
                </label>
                <input
                  type="url"
                  name="url"
                  defaultValue={editingProduct.url}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Price ($)
                </label>
                <input
                  type="number"
                  step="0.01"
                  name="target_price"
                  defaultValue={editingProduct.target_price}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div className="flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
                  disabled={connectionStatus === 'disconnected'}
                >
                  Save Changes
                </button>
                <button
                  type="button"
                  onClick={() => setEditingProduct(null)}
                  className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default PriceMonitorApp;