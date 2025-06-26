import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const ChartContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 1.5rem;
`;

const ChartTitle = styled.h3`
  margin-bottom: 1rem;
  color: #343a40;
  font-size: 1.1rem;
`;

const ChartControls = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
`;

const PeriodButton = styled.button`
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: ${props => props.active ? '#007bff' : 'white'};
  color: ${props => props.active ? 'white' : '#495057'};
  cursor: pointer;
  font-size: 0.9rem;
  
  &:hover {
    background: ${props => props.active ? '#0056b3' : '#f8f9fa'};
  }
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
`;

const MetricCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
`;

const MetricValue = styled.div`
  font-size: 2rem;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 0.5rem;
`;

const MetricLabel = styled.div`
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
`;

const MetricChange = styled.div`
  font-size: 0.8rem;
  color: ${props => props.positive ? '#28a745' : '#dc3545'};
`;

const RevenueChart = ({ artistId }) => {
  const [period, setPeriod] = useState('7d');
  const [chartType, setChartType] = useState('line');
  const [data, setData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  // モックデータ生成
  const generateMockData = (days) => {
    const labels = [];
    const revenues = [];
    const sales = [];
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      labels.push(date.toLocaleDateString('ja-JP', { 
        month: 'short', 
        day: 'numeric' 
      }));
      
      // ランダムな収益データ
      revenues.push(Math.random() * 10000 + 1000);
      sales.push(Math.floor(Math.random() * 50 + 5));
    }
    
    return { labels, revenues, sales };
  };

  const generateMockMetrics = () => {
    return {
      totalRevenue: 156890,
      totalSales: 342,
      averagePrice: 458,
      topTrack: 'Summer Vibes',
      revenueChange: +12.5,
      salesChange: +8.3,
      priceChange: +3.7
    };
  };

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      // 実際のAPIコールに置き換え
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const days = period === '7d' ? 7 : period === '30d' ? 30 : 90;
      const mockData = generateMockData(days);
      const mockMetrics = generateMockMetrics();
      
      setData(mockData);
      setMetrics(mockMetrics);
      setLoading(false);
    };
    
    fetchData();
  }, [period, artistId]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return '¥' + value.toLocaleString();
          }
        }
      }
    }
  };

  const lineChartData = data ? {
    labels: data.labels,
    datasets: [
      {
        label: '売上',
        data: data.revenues,
        borderColor: '#007bff',
        backgroundColor: 'rgba(0, 123, 255, 0.1)',
        fill: true,
        tension: 0.4,
      }
    ]
  } : null;

  const barChartData = data ? {
    labels: data.labels,
    datasets: [
      {
        label: '売上数',
        data: data.sales,
        backgroundColor: '#28a745',
        borderColor: '#1e7e34',
        borderWidth: 1,
      }
    ]
  } : null;

  const doughnutData = {
    labels: ['デジタル販売', 'ストリーミング', 'その他'],
    datasets: [
      {
        data: [70, 25, 5],
        backgroundColor: ['#007bff', '#28a745', '#ffc107'],
        borderWidth: 2,
        borderColor: '#fff'
      }
    ]
  };

  if (loading) {
    return <div>読み込み中...</div>;
  }

  return (
    <>
      {metrics && (
        <MetricsGrid>
          <MetricCard>
            <MetricValue>¥{metrics.totalRevenue.toLocaleString()}</MetricValue>
            <MetricLabel>総売上</MetricLabel>
            <MetricChange positive={metrics.revenueChange > 0}>
              {metrics.revenueChange > 0 ? '+' : ''}{metrics.revenueChange}%
            </MetricChange>
          </MetricCard>
          
          <MetricCard>
            <MetricValue>{metrics.totalSales}</MetricValue>
            <MetricLabel>総売上数</MetricLabel>
            <MetricChange positive={metrics.salesChange > 0}>
              {metrics.salesChange > 0 ? '+' : ''}{metrics.salesChange}%
            </MetricChange>
          </MetricCard>
          
          <MetricCard>
            <MetricValue>¥{metrics.averagePrice}</MetricValue>
            <MetricLabel>平均価格</MetricLabel>
            <MetricChange positive={metrics.priceChange > 0}>
              {metrics.priceChange > 0 ? '+' : ''}{metrics.priceChange}%
            </MetricChange>
          </MetricCard>
          
          <MetricCard>
            <MetricValue>{metrics.topTrack}</MetricValue>
            <MetricLabel>人気楽曲</MetricLabel>
            <MetricChange positive={true}>
              トップセラー
            </MetricChange>
          </MetricCard>
        </MetricsGrid>
      )}

      <ChartContainer>
        <ChartTitle>売上推移</ChartTitle>
        <ChartControls>
          <PeriodButton 
            active={period === '7d'} 
            onClick={() => setPeriod('7d')}
          >
            7日間
          </PeriodButton>
          <PeriodButton 
            active={period === '30d'} 
            onClick={() => setPeriod('30d')}
          >
            30日間
          </PeriodButton>
          <PeriodButton 
            active={period === '90d'} 
            onClick={() => setPeriod('90d')}
          >
            90日間
          </PeriodButton>
          
          <PeriodButton 
            active={chartType === 'line'} 
            onClick={() => setChartType('line')}
          >
            線グラフ
          </PeriodButton>
          <PeriodButton 
            active={chartType === 'bar'} 
            onClick={() => setChartType('bar')}
          >
            棒グラフ
          </PeriodButton>
        </ChartControls>
        
        <div style={{ height: '400px' }}>
          {chartType === 'line' && lineChartData && (
            <Line data={lineChartData} options={chartOptions} />
          )}
          {chartType === 'bar' && barChartData && (
            <Bar data={barChartData} options={chartOptions} />
          )}
        </div>
      </ChartContainer>

      <ChartContainer>
        <ChartTitle>収益内訳</ChartTitle>
        <div style={{ height: '300px', maxWidth: '400px', margin: '0 auto' }}>
          <Doughnut data={doughnutData} options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'bottom',
              }
            }
          }} />
        </div>
      </ChartContainer>
    </>
  );
};

export default RevenueChart;