import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createEvent, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('../api/hardware.js', () => ({
  fetchHardware: vi.fn(),
  checkinHardware: vi.fn(),
  checkoutHardware: vi.fn(),
  createHardwareSet: vi.fn(),
}));

import { checkinHardware, checkoutHardware, createHardwareSet, fetchHardware } from '../api/hardware.js';
import Availability from '../components/Availability.js';
import Capacity from '../components/Capacity.js';
import MyCheckedOut from '../components/MyCheckedOut.js';
import CheckIn from '../components/CheckIn.js';
import CheckOut from '../components/CheckOut.js';
import CreateHardwareSet from '../components/CreateHardwareSet.js';
import HardwareSet from '../components/HardwareSet.js';
import QuantityAction from '../components/QuantityAction.js';
import ResourceView from '../components/Project.js';

beforeEach(() => {
  vi.resetAllMocks();
});

describe('Availability, Capacity, and MyCheckedOut', () => {
  it('Availability shows its label and value, including zero', () => {
    render(<Availability available={0} />);
    expect(screen.getByText('Available')).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('Capacity shows its label and value', () => {
    render(<Capacity capacity={12} />);
    expect(screen.getByText('Capacity')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
  });

  it('MyCheckedOut shows its label and value, including zero', () => {
    render(<MyCheckedOut myCheckedOut={0} />);
    expect(screen.getByText("You've Checked Out")).toBeInTheDocument();
    expect(screen.getByText('0')).toBeInTheDocument();
  });
});

describe('QuantityAction', () => {
  function setup(overrides = {}) {
    const props = {
      label: 'Do It',
      busyLabel: 'Doing...',
      action: vi.fn().mockResolvedValue(undefined),
      describeError: (error) => `described: ${error.message}`,
      onChanged: vi.fn().mockResolvedValue(undefined),
      ...overrides,
    };
    render(<QuantityAction {...props} />);
    return props;
  }

  it('starts at quantity 1 and submits the numeric quantity then reloads', async () => {
    const props = setup();
    const input = screen.getByLabelText('Do It');
    expect(input).toHaveValue(1);

    await userEvent.clear(input);
    await userEvent.type(input, '4');
    await userEvent.click(screen.getByRole('button', { name: 'Do It' }));

    expect(props.action).toHaveBeenCalledWith(4);
    expect(typeof props.action.mock.calls[0][0]).toBe('number');
    await waitFor(() => expect(props.onChanged).toHaveBeenCalledTimes(1));
  });

  it('disables the button and shows the busy label while the action is in flight', async () => {
    let finish;
    const action = vi.fn(() => new Promise((resolve) => { finish = resolve; }));
    setup({ action });

    await userEvent.click(screen.getByRole('button', { name: 'Do It' }));

    const busyButton = await screen.findByRole('button', { name: 'Doing...' });
    expect(busyButton).toBeDisabled();

    finish();
    const idleButton = await screen.findByRole('button', { name: 'Do It' });
    expect(idleButton).toBeEnabled();
  });

  it('shows the described error as an alert and does not reload when the action fails', async () => {
    const props = setup({ action: vi.fn().mockRejectedValue(new Error('boom')) });

    await userEvent.click(screen.getByRole('button', { name: 'Do It' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('described: boom');
    expect(props.onChanged).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Do It' })).toBeEnabled();
  });

  it('caps the input at max when given', () => {
    setup({ max: 5 });
    expect(screen.getByLabelText('Do It')).toHaveAttribute('max', '5');
  });

  it('leaves the input uncapped when no max is given', () => {
    setup();
    expect(screen.getByLabelText('Do It')).not.toHaveAttribute('max');
  });

  it('disables the input and button outright when max is below 1', () => {
    setup({ max: 0 });
    expect(screen.getByLabelText('Do It')).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Do It' })).toBeDisabled();
  });

  it('clears a previous error when the next attempt succeeds', async () => {
    const action = vi
      .fn()
      .mockRejectedValueOnce(new Error('boom'))
      .mockResolvedValueOnce(undefined);
    setup({ action });

    await userEvent.click(screen.getByRole('button', { name: 'Do It' }));
    expect(await screen.findByRole('alert')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Do It' }));
    await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument());
  });

  it('declares a whole-number input with a minimum of 1', () => {
    setup();
    const input = screen.getByLabelText('Do It');
    expect(input).toHaveAttribute('type', 'number');
    expect(input).toHaveAttribute('min', '1');
    expect(input).toHaveAttribute('step', '1');
  });

  it('prevents the browser from submitting the form natively', () => {
    setup();
    const form = screen.getByRole('button', { name: 'Do It' }).closest('form');
    const event = createEvent.submit(form);
    fireEvent(form, event);
    expect(event.defaultPrevented).toBe(true);
  });

  it('keeps the entered quantity after a successful action', async () => {
    setup();
    const input = screen.getByLabelText('Do It');
    await userEvent.clear(input);
    await userEvent.type(input, '7');
    await userEvent.click(screen.getByRole('button', { name: 'Do It' }));

    await waitFor(() => expect(input).toHaveValue(7));
  });
});

describe('CheckOut', () => {
  const props = { projectId: 'P1', userId: 'alice', hwSetName: 'HWSet1' };

  it('calls checkoutHardware with the full payload and reloads', async () => {
    checkoutHardware.mockResolvedValue({});
    const onChanged = vi.fn().mockResolvedValue(undefined);
    render(<CheckOut {...props} onChanged={onChanged} />);

    await userEvent.clear(screen.getByLabelText('Check Out'));
    await userEvent.type(screen.getByLabelText('Check Out'), '3');
    await userEvent.click(screen.getByRole('button', { name: 'Check Out' }));

    expect(checkoutHardware).toHaveBeenCalledWith({
      projectId: 'P1',
      userId: 'alice',
      hwSetName: 'HWSet1',
      quantity: 3,
    });
    await waitFor(() => expect(onChanged).toHaveBeenCalled());
  });

  it('says how many are available when checking out too many', async () => {
    checkoutHardware.mockRejectedValue(Object.assign(new Error('insufficient_stock'), { onHand: 2, requested: 9 }));
    render(<CheckOut {...props} onChanged={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check Out' }));

    expect(await screen.findByRole('alert')).toHaveTextContent("Only 2 available -- can't check out 9.");
  });

  it('reports zero available rather than falling through to the raw error code', async () => {
    checkoutHardware.mockRejectedValue(Object.assign(new Error('insufficient_stock'), { onHand: 0, requested: 1 }));
    render(<CheckOut {...props} onChanged={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check Out' }));

    expect(await screen.findByRole('alert')).toHaveTextContent("Only 0 available -- can't check out 1.");
  });

  it('asks for a whole number when the server rejects the quantity', async () => {
    checkoutHardware.mockRejectedValue(Object.assign(new Error('invalid_input'), { field: 'quantity' }));
    render(<CheckOut {...props} onChanged={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check Out' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Enter a whole number of 1 or more.');
  });

  it('shows the raw message for any other error', async () => {
    checkoutHardware.mockRejectedValue(new Error('not_a_project_member'));
    render(<CheckOut {...props} onChanged={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check Out' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('not_a_project_member');
  });

  it('caps the quantity input at the units available, not a fixed number', () => {
    render(<CheckOut {...props} available={4} onChanged={vi.fn()} />);
    expect(screen.getByLabelText('Check Out')).toHaveAttribute('max', '4');
  });

  it('disables checkout when nothing is available', () => {
    render(<CheckOut {...props} available={0} onChanged={vi.fn()} />);
    expect(screen.getByRole('button', { name: 'Check Out' })).toBeDisabled();
  });
});

describe('CheckIn', () => {
  const props = { projectId: 'P1', userId: 'alice', hwSetName: 'HWSet1' };

  it('calls checkinHardware with the full payload and reloads', async () => {
    checkinHardware.mockResolvedValue({});
    const onChanged = vi.fn().mockResolvedValue(undefined);
    render(<CheckIn {...props} onChanged={onChanged} />);

    await userEvent.clear(screen.getByLabelText('Check In'));
    await userEvent.type(screen.getByLabelText('Check In'), '2');
    await userEvent.click(screen.getByRole('button', { name: 'Check In' }));

    expect(checkinHardware).toHaveBeenCalledWith({
      projectId: 'P1',
      userId: 'alice',
      hwSetName: 'HWSet1',
      quantity: 2,
    });
    await waitFor(() => expect(onChanged).toHaveBeenCalled());
  });

  it('says how many are checked out when checking in too many', async () => {
    checkinHardware.mockRejectedValue(
      Object.assign(new Error('checkin_exceeds_checked_out'), { checkedOut: 2, requested: 5 })
    );
    render(<CheckIn {...props} onChanged={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check In' }));

    expect(await screen.findByRole('alert')).toHaveTextContent("Only 2 checked out -- can't check in 5.");
  });

  it('reports zero checked out rather than the raw error code', async () => {
    checkinHardware.mockRejectedValue(
      Object.assign(new Error('checkin_exceeds_checked_out'), { checkedOut: 0, requested: 1 })
    );
    render(<CheckIn {...props} onChanged={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check In' }));

    expect(await screen.findByRole('alert')).toHaveTextContent("Only 0 checked out -- can't check in 1.");
  });

  it('asks for a whole number when the server rejects the quantity', async () => {
    checkinHardware.mockRejectedValue(Object.assign(new Error('invalid_input'), { field: 'quantity' }));
    render(<CheckIn {...props} onChanged={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check In' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Enter a whole number of 1 or more.');
  });

  it('shows the raw message for any other error', async () => {
    checkinHardware.mockRejectedValue(new Error('hardware_set_not_found'));
    render(<CheckIn {...props} onChanged={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check In' }));

    expect(await screen.findByRole('alert')).toHaveTextContent('hardware_set_not_found');
  });

  it('caps the quantity input at the units checked out, not a fixed number', () => {
    render(<CheckIn {...props} checkedOut={5} onChanged={vi.fn()} />);
    expect(screen.getByLabelText('Check In')).toHaveAttribute('max', '5');
  });

  it('disables check-in when nothing is checked out', () => {
    render(<CheckIn {...props} checkedOut={0} onChanged={vi.fn()} />);
    expect(screen.getByRole('button', { name: 'Check In' })).toBeDisabled();
  });
});

describe('HardwareSet', () => {
  it('shows the set name and its five components in order', () => {
    const hwSet = { hwSetName: 'HWSet1', capacity: 10, available: 6, myCheckedOut: 4 };
    render(<HardwareSet projectId="P1" userId="alice" hwSet={hwSet} onChanged={vi.fn()} />);

    const region = screen.getByRole('region', { name: 'HWSet1' });
    expect(screen.getByRole('heading', { name: 'HWSet1' })).toBeInTheDocument();
    const labels = Array.from(region.querySelectorAll('.hw-cell__label')).map((node) =>
      node.textContent.replace(/\d+$/, '').trim()
    );
    expect(labels).toEqual(['Available', 'Capacity', "You've Checked Out", 'Check In', 'Check Out']);
    expect(region).toHaveTextContent('6');
    expect(region).toHaveTextContent('10');
    expect(region).toHaveTextContent('4');
  });

  it('wires both actions to this set, project, and user', async () => {
    checkinHardware.mockResolvedValue({});
    checkoutHardware.mockResolvedValue({});
    // available > 0 and myCheckedOut > 0 so both actions have something
    // valid to do -- each control disables itself at 0, per
    // QuantityAction's own tests.
    const hwSet = { hwSetName: 'HWSet2', capacity: 5, available: 3, myCheckedOut: 2 };
    render(<HardwareSet projectId="P9" userId="bob" hwSet={hwSet} onChanged={vi.fn().mockResolvedValue()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Check In' }));
    await userEvent.click(screen.getByRole('button', { name: 'Check Out' }));

    const expected = { projectId: 'P9', userId: 'bob', hwSetName: 'HWSet2', quantity: 1 };
    expect(checkinHardware).toHaveBeenCalledWith(expected);
    expect(checkoutHardware).toHaveBeenCalledWith(expected);
  });

  it("caps Check In at myCheckedOut (this user's own holding), not capacity - available", () => {
    // Someone ELSE holds most of what's checked out -- capacity(10) -
    // available(2) = 8 checked out project-wide, but THIS user only
    // personally holds 3. The old (buggy) behavior would have capped
    // Check In at 8, letting this user check in units they never checked
    // out themselves.
    const hwSet = { hwSetName: 'HWSet3', capacity: 10, available: 2, myCheckedOut: 3 };
    render(<HardwareSet projectId="P1" userId="alice" hwSet={hwSet} onChanged={vi.fn()} />);

    expect(screen.getByLabelText('Check In')).toHaveAttribute('max', '3');
    expect(screen.getByLabelText('Check Out')).toHaveAttribute('max', '2');
  });

  it("shows a different user's own checked-out figure, not the project-wide total", () => {
    const hwSet = { hwSetName: 'HWSet4', capacity: 10, available: 2, myCheckedOut: 0 };
    render(<HardwareSet projectId="P1" userId="bob" hwSet={hwSet} onChanged={vi.fn()} />);

    // bob holds none of the 8 checked out project-wide -- Check In is
    // correctly disabled for him, even though plenty is checked out
    // overall (by someone else).
    expect(screen.getByRole('button', { name: 'Check In' })).toBeDisabled();
  });
});

describe('CreateHardwareSet', () => {
  it('submits the name and starting capacity, scoped to this project and user', async () => {
    createHardwareSet.mockResolvedValue({ hardwareSet: { hwSetName: 'NewSet', capacity: 10 } });
    const onCreated = vi.fn().mockResolvedValue();
    render(<CreateHardwareSet projectId="P1" userId="alice" onCreated={onCreated} />);

    await userEvent.type(screen.getByLabelText('Name'), 'NewSet');
    await userEvent.type(screen.getByLabelText('Starting capacity'), '10');
    await userEvent.click(screen.getByRole('button', { name: 'Add hardware set' }));

    expect(createHardwareSet).toHaveBeenCalledWith({
      projectId: 'P1',
      userId: 'alice',
      hwSetName: 'NewSet',
      capacity: 10,
    });
    expect(onCreated).toHaveBeenCalledTimes(1);
  });

  it('clears the form after a successful create', async () => {
    createHardwareSet.mockResolvedValue({ hardwareSet: { hwSetName: 'NewSet', capacity: 10 } });
    render(<CreateHardwareSet projectId="P1" userId="alice" onCreated={vi.fn().mockResolvedValue()} />);

    await userEvent.type(screen.getByLabelText('Name'), 'NewSet');
    await userEvent.type(screen.getByLabelText('Starting capacity'), '10');
    await userEvent.click(screen.getByRole('button', { name: 'Add hardware set' }));

    await waitFor(() => expect(screen.getByLabelText('Name')).toHaveValue(''));
    expect(screen.getByLabelText('Starting capacity')).toHaveValue(null);
  });

  it('shows a friendly message and does not clear the form when the server rejects the capacity', async () => {
    // A value that passes the input's own min="1" constraint (so the
    // native submit isn't blocked before this component's handler runs)
    // but that the server rejects anyway -- e.g. a second tab racing a
    // capacity that's since been invalidated some other way.
    const error = new Error('invalid_input');
    error.field = 'capacity';
    createHardwareSet.mockRejectedValue(error);
    const onCreated = vi.fn();
    render(<CreateHardwareSet projectId="P1" userId="alice" onCreated={onCreated} />);

    await userEvent.type(screen.getByLabelText('Name'), 'NewSet');
    await userEvent.type(screen.getByLabelText('Starting capacity'), '5');
    await userEvent.click(screen.getByRole('button', { name: 'Add hardware set' }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Starting capacity must be a whole number of 1 or more.'
    );
    expect(onCreated).not.toHaveBeenCalled();
    expect(screen.getByLabelText('Name')).toHaveValue('NewSet');
  });

  it('disables the submit button while the request is in flight', async () => {
    let resolveCreate;
    createHardwareSet.mockReturnValue(
      new Promise((resolve) => {
        resolveCreate = resolve;
      })
    );
    render(<CreateHardwareSet projectId="P1" userId="alice" onCreated={vi.fn().mockResolvedValue()} />);

    await userEvent.type(screen.getByLabelText('Name'), 'NewSet');
    await userEvent.type(screen.getByLabelText('Starting capacity'), '10');
    await userEvent.click(screen.getByRole('button', { name: 'Add hardware set' }));

    expect(screen.getByRole('button', { name: 'Adding...' })).toBeDisabled();
    resolveCreate({ hardwareSet: { hwSetName: 'NewSet', capacity: 10 } });
    await screen.findByRole('button', { name: 'Add hardware set' });
  });
});

describe('ResourceView', () => {
  const sets = [
    { hwSetName: 'HWSet1', capacity: 10, available: 10 },
    { hwSetName: 'HWSet2', capacity: 20, available: 15 },
  ];

  it('shows a loading message, then one card per set in the order received', async () => {
    fetchHardware.mockResolvedValue({ hardwareSets: sets });
    render(<ResourceView projectId="P1" userId="alice" />);

    expect(screen.getByText('Loading hardware resources...')).toBeInTheDocument();
    const regions = await screen.findAllByRole('region');
    expect(regions.map((region) => region.getAttribute('aria-label'))).toEqual(['HWSet1', 'HWSet2']);
    expect(fetchHardware).toHaveBeenCalledWith('P1', 'alice');
  });

  it('says so when the project has no hardware sets, but still offers the create form', async () => {
    fetchHardware.mockResolvedValue({ hardwareSets: [] });
    render(<ResourceView projectId="P1" userId="alice" />);

    expect(await screen.findByText('No hardware sets in this project yet.')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Add a hardware set' })).toBeInTheDocument();
  });

  it('creating a hardware set reloads the list', async () => {
    fetchHardware
      .mockResolvedValueOnce({ hardwareSets: [] })
      .mockResolvedValueOnce({ hardwareSets: [{ hwSetName: 'NewSet', capacity: 10, available: 10 }] });
    createHardwareSet.mockResolvedValue({ hardwareSet: { hwSetName: 'NewSet', capacity: 10 } });
    render(<ResourceView projectId="P1" userId="alice" />);
    await screen.findByText('No hardware sets in this project yet.');

    await userEvent.type(screen.getByLabelText('Name'), 'NewSet');
    await userEvent.type(screen.getByLabelText('Starting capacity'), '10');
    await userEvent.click(screen.getByRole('button', { name: 'Add hardware set' }));

    expect(await screen.findByRole('region', { name: 'NewSet' })).toBeInTheDocument();
    expect(createHardwareSet).toHaveBeenCalledWith({
      projectId: 'P1',
      userId: 'alice',
      hwSetName: 'NewSet',
      capacity: 10,
    });
  });

  it('treats a response without hardwareSets as empty', async () => {
    fetchHardware.mockResolvedValue(null);
    render(<ResourceView projectId="P1" userId="alice" />);

    expect(await screen.findByText('No hardware sets in this project yet.')).toBeInTheDocument();
  });

  it('shows the error with a Retry button that refetches', async () => {
    fetchHardware
      .mockRejectedValueOnce(new Error('not_a_project_member'))
      .mockResolvedValueOnce({ hardwareSets: sets });
    render(<ResourceView projectId="P1" userId="alice" />);

    expect(await screen.findByText('not_a_project_member')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'Retry' }));

    expect(await screen.findByRole('region', { name: 'HWSet1' })).toBeInTheDocument();
    expect(fetchHardware).toHaveBeenCalledTimes(2);
  });

  it('refreshes the numbers after a checkout without unmounting the cards', async () => {
    fetchHardware
      .mockResolvedValueOnce({ hardwareSets: [{ hwSetName: 'HWSet1', capacity: 10, available: 10 }] })
      .mockResolvedValueOnce({ hardwareSets: [{ hwSetName: 'HWSet1', capacity: 10, available: 7 }] });
    checkoutHardware.mockResolvedValue({});
    render(<ResourceView projectId="P1" userId="alice" />);

    const region = await screen.findByRole('region', { name: 'HWSet1' });
    await userEvent.clear(screen.getByLabelText('Check Out'));
    await userEvent.type(screen.getByLabelText('Check Out'), '3');
    await userEvent.click(screen.getByRole('button', { name: 'Check Out' }));

    await waitFor(() => expect(region).toHaveTextContent('7'));
    expect(screen.queryByText('Loading hardware resources...')).not.toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'HWSet1' })).toBe(region);
  });

  it('refetches when the project or user changes', async () => {
    fetchHardware.mockResolvedValue({ hardwareSets: sets });
    const { rerender } = render(<ResourceView projectId="P1" userId="alice" />);
    await screen.findAllByRole('region');

    rerender(<ResourceView projectId="P2" userId="alice" />);
    await waitFor(() => expect(fetchHardware).toHaveBeenCalledWith('P2', 'alice'));

    rerender(<ResourceView projectId="P2" userId="bob" />);
    await waitFor(() => expect(fetchHardware).toHaveBeenCalledWith('P2', 'bob'));
  });
});
