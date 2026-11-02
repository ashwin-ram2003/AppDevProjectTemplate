import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchHardware } from '../api/hardware.js';
import CreateHardwareSet from './CreateHardwareSet.js';
import HardwareSet from './HardwareSet.js';

/**
 * ResourceView is the top-level presentational component for a project's
 * hardware resources. It fetches its own data through
 * client/src/api/hardware.js, but accepts session identity as props rather
 * than reading it from any global auth state -- Track A's session/auth layer
 * wires real values in here once it lands.
 *
 * Data source: fetches via client/src/api/hardware.js
 * No hard-coded fallback: this component renders nothing it was not given or told.
 *
 * @component
 * @param {Object} props
 * @param {string} props.projectId - The project whose hardware sets to load.
 *   No fallback/default; a real session must supply this.
 * @param {string} props.userId - The acting user's id, used for checkin/
 *   checkout calls. No fallback/default.
 */
export default function ResourceView({ projectId, userId }) {
  const [hardware, setHardware] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Only the most recently started load may update state; a slower, older
  // response must not overwrite newer data.
  const latestLoad = useRef(0);

  const loadHardware = useCallback(async () => {
    const thisLoad = ++latestLoad.current;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchHardware(projectId, userId);
      if (thisLoad === latestLoad.current) {
        setHardware(data);
      }
    } catch (fetchError) {
      if (thisLoad === latestLoad.current) {
        setError(fetchError.message);
      }
    } finally {
      if (thisLoad === latestLoad.current) {
        setLoading(false);
      }
    }
  }, [projectId, userId]);

  useEffect(() => {
    loadHardware();
  }, [loadHardware]);

  if (loading && hardware === null) {
    return <p>Loading hardware resources...</p>;
  }

  if (error) {
    return (
      <div>
        <p className="error-text">{error}</p>
        <button type="button" onClick={loadHardware}>
          Retry
        </button>
      </div>
    );
  }

  const hardwareSets = hardware ? hardware.hardwareSets : [];

  return (
    <div>
      <CreateHardwareSet projectId={projectId} userId={userId} onCreated={loadHardware} />
      {hardwareSets.length === 0 ? (
        <p className="muted-text">No hardware sets in this project yet.</p>
      ) : (
        <div className="hw-set-list">
          {hardwareSets.map((hwSet) => (
            <HardwareSet
              key={hwSet.hwSetName}
              projectId={projectId}
              userId={userId}
              hwSet={hwSet}
              onChanged={loadHardware}
            />
          ))}
        </div>
      )}
    </div>
  );
}
