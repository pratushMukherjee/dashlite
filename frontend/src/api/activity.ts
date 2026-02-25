import apiClient from './client';
import type { ActivityFeedResponse, ActivityStatsResponse } from '../types';

export async function getActivityFeed(skip = 0, limit = 20): Promise<ActivityFeedResponse> {
  const { data } = await apiClient.get('/activity/feed', { params: { skip, limit } });
  return data;
}

export async function getActivityStats(): Promise<ActivityStatsResponse> {
  const { data } = await apiClient.get('/activity/stats');
  return data;
}
