import { expect, it, vi } from 'vitest';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

vi.mock('../api/hardware.js', () => ({
  fetchHardware: vi.fn(),
  checkinHardware: vi.fn(),
  checkoutHardware: vi.fn(),
}));
import { checkinHardware, checkoutHardware, fetchHardware } from '../api/hardware.js';
import ResourceView from '../components/Project.js';

const snapshot = (available) => ({ hardwareSets: [{ hwSetName: 'HWSet1', capacity: 10, available }] });

it('ignores a slower, older reload response that arrives after a newer one', async () => {
  let resolveFirstReload;
  fetchHardware
    // initial load: available 9 of 10 (1 already checked out), so Check In
    // has something valid to check back in from the start -- an
    // all-available fixture would leave Check In correctly disabled and
    // its click below a no-op, under-draining this mock queue and
    // bleeding into the next test.
    .mockResolvedValueOnce(snapshot(9))
    .mockImplementationOnce(() => new Promise((resolve) => { resolveFirstReload = resolve; })) // reload after checkout (slow)
    .mockResolvedValueOnce(snapshot(7)); // reload after check in (fast, newest state)
  checkoutHardware.mockResolvedValue({});
  checkinHardware.mockResolvedValue({});

  render(<ResourceView projectId="P1" userId="alice" />);
  const region = await screen.findByRole('region', { name: 'HWSet1' });

  await userEvent.click(screen.getByRole('button', { name: 'Check Out' })); // server state: 8, response pending
  await userEvent.click(screen.getByRole('button', { name: 'Check In' })); // server state: 7, newest snapshot = 7
  await waitFor(() => expect(region).toHaveTextContent('7'));

  resolveFirstReload(snapshot(8)); // the OLDER response arrives last
  await new Promise((resolve) => setTimeout(resolve, 20));

  expect(region).toHaveTextContent('7'); // newest data should win
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

it('keeps showing the loading message when an outdated first load finishes before the current one', async () => {
  const outdated = deferred();
  const current = deferred();
  fetchHardware.mockReturnValueOnce(outdated.promise).mockReturnValueOnce(current.promise);

  const { rerender } = render(<ResourceView projectId="P1" userId="alice" />);
  rerender(<ResourceView projectId="P2" userId="alice" />);

  await act(async () => {
    outdated.resolve(snapshot(3));
  });

  expect(screen.getByText('Loading hardware resources...')).toBeInTheDocument();
  expect(screen.queryByRole('region')).not.toBeInTheDocument();
  expect(screen.queryByText('No hardware sets in this project yet.')).not.toBeInTheDocument();

  await act(async () => {
    current.resolve(snapshot(9));
  });
  expect(await screen.findByRole('region', { name: 'HWSet1' })).toHaveTextContent('9');
});

it('ignores an outdated load that fails after a newer load succeeded', async () => {
  const outdated = deferred();
  fetchHardware.mockReturnValueOnce(outdated.promise).mockResolvedValueOnce(snapshot(9));

  const { rerender } = render(<ResourceView projectId="P1" userId="alice" />);
  rerender(<ResourceView projectId="P2" userId="alice" />);
  const region = await screen.findByRole('region', { name: 'HWSet1' });

  await act(async () => {
    outdated.reject(new Error('stale failure'));
  });

  expect(screen.queryByText('stale failure')).not.toBeInTheDocument();
  expect(screen.getByRole('region', { name: 'HWSet1' })).toBe(region);
});
