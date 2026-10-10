import { useCallback, useEffect, useRef, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import World from './World.jsx'
import Player from './Player.jsx'
import Minimap from './Minimap.jsx'
import TouchControls from './TouchControls.jsx'
import { EYE, SPAWN } from './layout.js'

export default function App() {
  const [locked, setLocked] = useState(false)
  const [where, setWhere] = useState('')
  const [showMap, setShowMap] = useState(true)
  const lockRef = useRef()
  const mapRef = useRef()
  const onLock = useCallback((v) => setLocked(v), [])
  const onWhere = useCallback((w) => setWhere(w), [])
  // phones have no pointer lock, so they get a joystick + drag-to-look instead
  const [isTouch] = useState(() => matchMedia('(pointer: coarse)').matches) // phones + tablets; touchscreen laptops still get mouse mode
  const [touchOn, setTouchOn] = useState(false)
  const touchRef = useRef({ active: false, move: [0, 0], look: [0, 0], jump: false })
  const setTouch = (on) => {
    touchRef.current.active = on
    touchRef.current.move = [0, 0]
    setTouchOn(on)
  }
  const playing = locked || touchOn
  useEffect(() => {
    const k = (e) => e.code === 'KeyM' && setShowMap((v) => !v)
    window.addEventListener('keydown', k)
    return () => window.removeEventListener('keydown', k)
  }, [])

  return (
    <>
      <Canvas
        camera={{ fov: 72, near: 0.05, far: 800, position: [SPAWN.x, EYE, SPAWN.z] }}
        dpr={[1, 1.75]}
      >
        <World />
        <Player lockRef={lockRef} mapRef={mapRef} touchRef={touchRef} onLock={onLock} onWhere={onWhere} />
      </Canvas>

      <div className="where">
        <span className="dot" />
        {where}
      </div>
      <div className={showMap ? 'mapwrap' : 'mapwrap hidden'}>
        <Minimap drawRef={mapRef} />
      </div>
      <button className="maptoggle" onClick={() => setShowMap((s) => !s)}>
        {showMap ? '🗺️ hide map' : '🗺️ map'}
      </button>
      {playing && <div className="crosshair" />}
      {touchOn && <TouchControls touchRef={touchRef} onPause={() => setTouch(false)} />}

      {!playing && (
        <div className="overlay" onClick={() => (isTouch ? setTouch(true) : lockRef.current?.())}>
          <div className="card">
            <div className="kicker">🏫 Welcome, explorer!</div>
            <h1>Let's Explore!</h1>
            <p className="sub">Walk around a real school building at Yale. Peek into the round classrooms and say hi to the friends in the courtyard!</p>
            <div className="mission">
              <span className="mission-icon">🐶</span>
              <span>
                <b>Your mission:</b> find <b>Handsome Dan</b>, the Yale bulldog! He's the <b className="bluedot">blue dot</b> on the map.
              </span>
            </div>
            <button className="go">🚀 {isTouch ? "Tap to start!" : "Let's go!"}</button>
            {!isTouch && (
              <button
                className="go alt"
                onClick={(e) => {
                  e.stopPropagation()
                  setTouch(true)
                }}
              >
                🕹️ Use a joystick instead
              </button>
            )}
            {isTouch ? (
              <div className="keys">
                <span>👍 <b>Left thumb</b> walk</span>
                <span>👆 <b>Drag</b> look around</span>
                <span>🦘 <b>Jump</b> button</span>
              </div>
            ) : (
              <div className="keys">
                <span>⬆️⬇️⬅️➡️ <b>Arrows</b> walk</span>
                <span>🖱️ <b>Mouse</b> look around</span>
                <span>🦘 <b>Space</b> jump</span>
                <span>🗺️ <b>M</b> map</span>
                <span>⏸️ <b>Esc</b> stop</span>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}
