import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  checkinHardware,
  checkoutHardware,
  fetchHardware,
  releaseRequest,
  renameHardwareSet,
  requestHardware,
  setHardwareSetActive,
} from '../api/hardware.js';

function jsonResponse(status, body) {
  return { ok: status >= 200 && status < 300, status, json: async () => body };
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn());
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('fetchHardware', () => {
  it('GETs /api/hardware with projectId and userId query params and returns the body', async () => {
    fetch.mockResolvedValue(jsonResponse(200, { hardwareSets: [{ hwSetName: 'HWSet1' }] }));

    const data = await fetchHardware('P 1', 'alice');

    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith('/api/hardware?projectId=P+1&userId=alice');
    expect(data).toEqual({ hardwareSets: [{ hwSetName: 'HWSet1' }] });
  });

  it('throws an Error carrying the server error code on a non-ok response', async () => {
    fetch.mockResolvedValue(jsonResponse(403, { error: 'not_a_project_member' }));

    await expect(fetchHardware('P1', 'mallory')).rejects.toThrow('not_a_project_member');
  });
});

describe('error responses', () => {
  it('falls back to a status message when the body has no error field', async () => {
    fetch.mockResolvedValue(jsonResponse(500, {}));

    await expect(checkoutHardware({})).rejects.toThrow('Request failed with status 500');
  });

  it('falls back to a status message when the body is not JSON', async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => {
        throw new Error('not json');
      },
    });

    await expect(checkoutHardware({})).rejects.toThrow('Request failed with status 502');
  });

  it('falls back to a status message when the body is null', async () => {
    fetch.mockResolvedValue(jsonResponse(500, null));

    await expect(checkoutHardware({})).rejects.toThrow('Request failed with status 500');
  });

  it('carries onHand, checkedOut, requested, and field when present', async () => {
    fetch.mockResolvedValue(
      jsonResponse(409, {
        error: 'insufficient_stock',
        onHand: 2,
        checkedOut: 3,
        requested: 9,
        field: 'quantity',
      })
    );

    const error = await checkoutHardware({}).catch((caught) => caught);

    expect(error.onHand).toBe(2);
    expect(error.checkedOut).toBe(3);
    expect(error.requested).toBe(9);
    expect(error.field).toBe('quantity');
  });

  it('carries a zero onHand (zero is a number, not absent)', async () => {
    fetch.mockResolvedValue(jsonResponse(409, { error: 'insufficient_stock', onHand: 0, requested: 1 }));

    const error = await checkoutHardware({}).catch((caught) => caught);

    expect(error.onHand).toBe(0);
  });

  it('leaves the numeric fields undefined when the body lacks them or they are not numbers', async () => {
    fetch.mockResolvedValue(
      jsonResponse(409, { error: 'x', onHand: '5', checkedOut: '5', requested: '5' })
    );

    const error = await checkoutHardware({}).catch((caught) => caught);

    expect(error.onHand).toBeUndefined();
    expect(error.checkedOut).toBeUndefined();
    expect(error.requested).toBeUndefined();
    expect(error.field).toBeUndefined();
  });
});

describe('mutating calls', () => {
  const payload = { projectId: 'P1', userId: 'alice', hwSetName: 'HWSet1', quantity: 3 };

  it.each([
    ['checkinHardware', checkinHardware, '/api/hardware/checkin'],
    ['checkoutHardware', checkoutHardware, '/api/hardware/checkout'],
    ['requestHardware', requestHardware, '/api/hardware/request'],
    ['releaseRequest', releaseRequest, '/api/hardware/release'],
    ['renameHardwareSet', renameHardwareSet, '/api/hardware/rename'],
    ['setHardwareSetActive', setHardwareSetActive, '/api/hardware/set_active'],
  ])('%s POSTs the JSON payload to %s and returns the body', async (_name, call, path) => {
    fetch.mockResolvedValue(jsonResponse(200, { hardwareSet: { hwSetName: 'HWSet1' } }));

    const data = await call(payload);

    expect(fetch).toHaveBeenCalledWith(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    expect(data).toEqual({ hardwareSet: { hwSetName: 'HWSet1' } });
  });
});
