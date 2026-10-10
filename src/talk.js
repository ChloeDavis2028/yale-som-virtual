// Who you can talk to in the 3D world. Shared by Professor, Player, App and ChatPanel.

// 3D roots (THREE.Object3D) the crosshair can click on; each has userData.talkId
export const TALKABLES = new Set()

// AI avatars you can chat with (ids match backend/people.py)
export const PEOPLE_INFO = {
  zaman: { name: 'Prof. Tauhid Zaman', course: 'MGT 409 · AI Foundations for Managers', room: 'Classroom 2200' },
}

// who you're chatting with right now (read every frame, so it's a plain object, not React state)
export const TALKING = { id: null }
