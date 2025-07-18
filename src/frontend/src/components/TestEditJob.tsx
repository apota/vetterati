import React, { useState } from 'react';
import { Button, Box, Typography, Alert } from '@mui/material';
import { jobService } from '../services/jobService';

const TestEditJob: React.FC = () => {
  const [result, setResult] = useState<string>('');
  const [error, setError] = useState<string>('');

  const testFetchJob = async () => {
    try {
      setError('');
      setResult('Fetching job...');
      
      // Use a known job ID
      const jobId = '81d20b7d-4acc-4cd0-b15d-7daf80195683';
      const job = await jobService.getJob(jobId);
      
      setResult(`Success! Job title: ${job.title}`);
    } catch (err: any) {
      console.error('Test error:', err);
      setError(`Error: ${err.message || 'Unknown error'}`);
    }
  };

  return (
    <Box sx={{ p: 2, border: '1px solid #ccc', m: 2 }}>
      <Typography variant="h6">Test Edit Job Functionality</Typography>
      <Button variant="contained" onClick={testFetchJob} sx={{ mt: 1, mb: 2 }}>
        Test Fetch Job
      </Button>
      
      {result && (
        <Typography variant="body2" sx={{ mb: 1 }}>
          {result}
        </Typography>
      )}
      
      {error && (
        <Alert severity="error">
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default TestEditJob;
