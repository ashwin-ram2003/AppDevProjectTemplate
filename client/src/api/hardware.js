// Thin wrapper around the Flask hardware routes. Components never call fetch directly.
import { post } from './http';

export const createHardwareSet = (hwSetName, initCapacity) =>
  post('/create_hardware_set', { hwSetName, initCapacity });

export const getHwInfo = (hwSetName) => post('/get_hw_info', { hwSetName });

// Returns [{ hwName, capacity, availability }, ...]
export async function getAllHardwareSets() {
  const { hwNames } = await post('/get_all_hw_names');
  return Promise.all(hwNames.map((name) => getHwInfo(name)));
}

// Both resolve to { message, availability } (the set's new availability).
// checkOut rejects when qty exceeds what's available; checkIn rejects when qty is
// more than the project has checked out.
export const checkOut = (projectId, hwSetName, userId, qty) =>
  post('/check_out', { projectId, hwSetName, userId, qty });

export const checkIn = (projectId, hwSetName, userId, qty) =>
  post('/check_in', { projectId, hwSetName, userId, qty });
