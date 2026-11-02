import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('../api/hardware.js', () => ({
  fetchHardware: vi.fn(),
  checkinHardware: vi.fn(),
  checkoutHardware: vi.fn(),
  createHardwareSet: vi.fn(),
  renameHardwareSet: vi.fn(),
  setHardwareSetActive: vi.fn(),
}));

import {
  checkoutHardware,
  fetchHardware,
  renameHardwareSet,
  setHardwareSetActive,
} from '../api/hardware.js';
import HardwareSetAdmin from '../components/HardwareSetAdmin.js';
import ResourceView from '../components/Project.js';

beforeEach(() => {
  vi.resetAllMocks();
});

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

function apiError(message, extra = {}) {
  return Object.assign(new Error(message), extra);
}

const baseSet = { hwSetName: 'HWSet1', capacity: 10, available: 10, myCheckedOut: 0, active: true };

function renderAdmin(hwSet = baseSet) {
  const onChanged = vi.fn().mockResolvedValue(undefined);
  render(<HardwareSetAdmin projectId="P1" userId="alice" hwSet={hwSet} onChanged={onChanged} />);
  return onChanged;
}

describe('HardwareSetAdmin rename', () => {
  it('Rename reveals a prefilled "New name" input; Cancel hides it and calls nothing', async () => {
    renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Rename' }));
    expect(screen.getByLabelText('New name')).toHaveValue('HWSet1');
    await userEvent.click(screen.getByRole('button', { name: 'Cancel' }));
    expect(screen.queryByLabelText('New name')).not.toBeInTheDocument();
    expect(renameHardwareSet).not.toHaveBeenCalled();
  });

  it('Save name sends the exact payload, reloads once and closes the form', async () => {
    renameHardwareSet.mockResolvedValue({});
    const onChanged = renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Rename' }));
    const input = screen.getByLabelText('New name');
    await userEvent.clear(input);
    await userEvent.type(input, 'Widgets');
    await userEvent.click(screen.getByRole('button', { name: 'Save name' }));
    expect(renameHardwareSet).toHaveBeenCalledWith({
      projectId: 'P1',
      userId: 'alice',
      hwSetName: 'HWSet1',
      newName: 'Widgets',
    });
    await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
    expect(screen.queryByLabelText('New name')).not.toBeInTheDocument();
  });

  it('disables the save button and shows Saving... while in flight', async () => {
    const pending = deferred();
    renameHardwareSet.mockReturnValue(pending.promise);
    renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Rename' }));
    await userEvent.click(screen.getByRole('button', { name: 'Save name' }));
    const saving = await screen.findByRole('button', { name: 'Saving...' });
    expect(saving).toBeDisabled();
    pending.resolve({});
    await waitFor(() => expect(screen.queryByRole('button', { name: 'Saving...' })).not.toBeInTheDocument());
  });

  it('shows the name-taken message, does not reload, and keeps the typed value', async () => {
    renameHardwareSet.mockRejectedValue(apiError('hardware_set_name_taken', { field: 'newName' }));
    const onChanged = renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Rename' }));
    const input = screen.getByLabelText('New name');
    await userEvent.clear(input);
    await userEvent.type(input, 'Other');
    await userEvent.click(screen.getByRole('button', { name: 'Save name' }));
    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Another hardware set in this project already uses that name.',
    );
    expect(onChanged).not.toHaveBeenCalled();
    expect(screen.getByLabelText('New name')).toHaveValue('Other');
  });

  it('shows "Name is required." for a newName field rejection', async () => {
    renameHardwareSet.mockRejectedValue(apiError('invalid_input', { field: 'newName' }));
    renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Rename' }));
    await userEvent.click(screen.getByRole('button', { name: 'Save name' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Name is required.');
  });

  it('shows any other error message raw', async () => {
    renameHardwareSet.mockRejectedValue(apiError('boom'));
    renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Rename' }));
    await userEvent.click(screen.getByRole('button', { name: 'Save name' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('boom');
  });
});

describe('HardwareSetAdmin activation', () => {
  it('Deactivate sends active: false and reloads', async () => {
    setHardwareSetActive.mockResolvedValue({});
    const onChanged = renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Deactivate' }));
    expect(setHardwareSetActive).toHaveBeenCalledWith({
      projectId: 'P1',
      userId: 'alice',
      hwSetName: 'HWSet1',
      active: false,
    });
    await waitFor(() => expect(onChanged).toHaveBeenCalledTimes(1));
  });

  it('in-use refusal shows the count and does not reload', async () => {
    setHardwareSetActive.mockRejectedValue(apiError('hardware_set_in_use', { checkedOut: 3 }));
    const onChanged = renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Deactivate' }));
    expect(await screen.findByRole('alert')).toHaveTextContent("Can't deactivate -- 3 still checked out.");
    expect(onChanged).not.toHaveBeenCalled();
  });

  it('an inactive set shows Reactivate, which sends active: true', async () => {
    setHardwareSetActive.mockResolvedValue({});
    renderAdmin({ ...baseSet, active: false });
    expect(screen.queryByRole('button', { name: 'Deactivate' })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Reactivate' }));
    expect(setHardwareSetActive).toHaveBeenCalledWith(expect.objectContaining({ active: true }));
  });

  it('a set with no active field shows Deactivate', () => {
    const { active, ...legacy } = baseSet;
    renderAdmin(legacy);
    expect(screen.getByRole('button', { name: 'Deactivate' })).toBeInTheDocument();
  });

  it('shows any other activation error raw', async () => {
    setHardwareSetActive.mockRejectedValue(apiError('weird'));
    renderAdmin();
    await userEvent.click(screen.getByRole('button', { name: 'Deactivate' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('weird');
  });
});

describe('ResourceView with admin controls', () => {
  const snap = (set) => ({ hardwareSets: [set] });

  it('a rename refreshes from the server and keeps the same card mounted', async () => {
    fetchHardware
      .mockResolvedValueOnce(snap({ _id: 'x1', ...baseSet }))
      .mockResolvedValueOnce(snap({ _id: 'x1', ...baseSet, hwSetName: 'Widgets' }));
    renameHardwareSet.mockResolvedValue({});
    render(<ResourceView projectId="P1" userId="alice" />);
    const region = await screen.findByRole('region', { name: 'HWSet1' });
    await userEvent.click(screen.getByRole('button', { name: 'Rename' }));
    await userEvent.click(screen.getByRole('button', { name: 'Save name' }));
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Widgets' })).toBeInTheDocument());
    expect(screen.getByRole('region', { name: 'Widgets' })).toBe(region);
  });

  it('a newer reload wins over an older slow one after a rename', async () => {
    const slow = deferred();
    fetchHardware
      .mockResolvedValueOnce(snap({ _id: 'x1', ...baseSet }))
      .mockImplementationOnce(() => slow.promise)
      .mockResolvedValueOnce(snap({ _id: 'x1', ...baseSet, hwSetName: 'Widgets' }));
    checkoutHardware.mockResolvedValue({});
    renameHardwareSet.mockResolvedValue({});
    render(<ResourceView projectId="P1" userId="alice" />);
    const region = await screen.findByRole('region', { name: 'HWSet1' });
    await userEvent.click(screen.getByRole('button', { name: 'Check Out' }));
    await userEvent.click(screen.getByRole('button', { name: 'Rename' }));
    await userEvent.click(screen.getByRole('button', { name: 'Save name' }));
    await waitFor(() => expect(screen.getByRole('heading', { name: 'Widgets' })).toBeInTheDocument());
    slow.resolve(snap({ _id: 'x1', ...baseSet }));
    await new Promise((resolve) => setTimeout(resolve, 20));
    expect(screen.getByRole('heading', { name: 'Widgets' })).toBeInTheDocument();
    expect(region).toBeInTheDocument();
  });

  it('deactivating refreshes the card into its inactive state from the server', async () => {
    fetchHardware
      .mockResolvedValueOnce(snap({ _id: 'x1', ...baseSet }))
      .mockResolvedValueOnce(snap({ _id: 'x1', ...baseSet, active: false }));
    setHardwareSetActive.mockResolvedValue({});
    render(<ResourceView projectId="P1" userId="alice" />);
    await screen.findByRole('region', { name: 'HWSet1' });
    expect(screen.queryByText('Inactive')).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Deactivate' }));
    expect(await screen.findByText('Inactive')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reactivate' })).toBeInTheDocument();
  });

  it('a refused deactivate keeps the card active and shows the message', async () => {
    fetchHardware.mockResolvedValueOnce(snap({ _id: 'x1', ...baseSet }));
    setHardwareSetActive.mockRejectedValue(apiError('hardware_set_in_use', { checkedOut: 2 }));
    render(<ResourceView projectId="P1" userId="alice" />);
    await screen.findByRole('region', { name: 'HWSet1' });
    await userEvent.click(screen.getByRole('button', { name: 'Deactivate' }));
    expect(await screen.findByRole('alert')).toHaveTextContent("Can't deactivate -- 2 still checked out.");
    expect(screen.queryByText('Inactive')).not.toBeInTheDocument();
    expect(fetchHardware).toHaveBeenCalledTimes(1);
  });
});
