#!/usr/bin/env python3
"""Patch script untuk menambahkan broadcast status functionality."""

import re

def patch_web_server():
    """Add broadcast status functionality to web_server.py"""
    
    with open('web_server.py', 'r') as f:
        content = f.read()
    
    # 1. Add requests import (check if not already there)
    if 'import requests' not in content:
        content = content.replace(
            'import queue\nfrom typing',
            'import queue\nimport requests\nfrom typing'
        )
        print("✓ Added requests import")
    else:
        print("✓ requests import already exists")
    
    # 2. Add broadcast_status_lock in __init__ (check if not already there)
    if 'self.broadcast_status_lock = asyncio.Lock()' not in content:
        content = content.replace(
            'self.broadcast_queue = queue.Queue(maxsize=10)',
            'self.broadcast_queue = queue.Queue(maxsize=10)\n        self.broadcast_status_lock = asyncio.Lock()'
        )
        print("✓ Added broadcast_status_lock")
    else:
        print("✓ broadcast_status_lock already exists")
    
    # 3. Add get_status() method (check if not already there)
    if 'async def get_status(self) -> dict:' not in content:
        get_status_method = '''    
    async def get_status(self) -> dict:
        """Get current system status."""
        return {
            'type': 'status',
            'armed': self.system.is_armed,
            'recording': self.system.is_recording,
            'muted': self.system.is_muted,
            'persons': self.system.person_count,
            'alerts': self.system.alert_count,
            'breach_active': self.system.breach_active,
            'breach_duration': int(time.time() - self.system.breach_start_time) if self.system.breach_active else 0,
            'confidence': self.system.confidence,
            'model': self.system.model_name,
            'skeleton': self.system.enable_skeleton,
            'face': self.system.enable_face,
            'motion': self.system.enable_motion,
            'heatmap': self.system.enable_heatmap,
            'night_vision': self.system.night_vision,
            'zones': self.system.zone_manager.get_zone_count() if self.system.zone_manager else 0,
            'faces': len(self.system.face_engine.known_names) if self.system.face_engine else 0,
            'clients': len(self.clients),
            'demo_mode': self.system.demo_mode,
            'camera_available': self.system.camera_available
        }
    
    async def broadcast_status(self):
        """Broadcast status update to all connected clients."""
        if not self.clients:
            return
        
        try:
            status = await self.get_status()
            message = json.dumps(status)
            
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
            logging.debug(f"[Status] Broadcasted to {len(self.clients)} clients")
        except Exception as e:
            logging.error(f"[Status] Broadcast error: {e}")
    
    '''
        
        # Insert before handle_command
        content = content.replace(
            '    async def handle_command(self, data: Dict, websocket):',
            get_status_method + '    async def handle_command(self, data: Dict, websocket):'
        )
        print("✓ Added get_status() and broadcast_status() methods")
    else:
        print("✓ get_status() and broadcast_status() methods already exist")
    
    # 4. Update get_status command to use new method
    if "cmd_type == 'get_status':" in content and "await self.get_status()" not in content:
        # Find and replace the inline status dict creation
        old_pattern = r'''if cmd_type == 'get_status':
            status = \{
                'type': 'status',
                'armed': self\.system\.is_armed,
                'recording': self\.system\.is_recording,
                'muted': self\.system\.is_muted,
                'persons': self\.system\.person_count,
                'alerts': self\.system\.alert_count,
                'breach_active': self\.system\.breach_active,
                'breach_duration': int\(time\.time\(\) - self\.system\.breach_start_time\) if self\.system\.breach_active else 0,
                'confidence': self\.system\.confidence,
                'model': self\.system\.model_name,
                'skeleton': self\.system\.enable_skeleton,
                'face': self\.system\.enable_face,
                'motion': self\.system\.enable_motion,
                'heatmap': self\.system\.enable_heatmap,
                'night_vision': self\.system\.night_vision,
                'zones': self\.system\.zone_manager\.get_zone_count\(\) if self\.system\.zone_manager else 0,
                'faces': len\(self\.system\.face_engine\.known_names\) if self\.system\.face_engine else 0,
                'clients': len\(self\.clients\),
                'demo_mode': self\.system\.demo_mode,
                'camera_available': self\.system\.camera_available
            \}
            await websocket\.send\(json\.dumps\(status\)\)'''
        
        new_code = '''if cmd_type == 'get_status':
            status = await self.get_status()
            await websocket.send(json.dumps(status))'''
        
        if re.search(old_pattern, content, re.MULTILINE | re.DOTALL):
            content = re.sub(old_pattern, new_code, content, flags=re.MULTILINE | re.DOTALL)
            print("✓ Updated get_status command to use get_status() method")
        else:
            print("✓ get_status command already uses get_status() method")
    
    # 5. Add broadcast_status() calls after state changes
    commands_to_broadcast = [
        ('toggle_arm', "self.system.toggle_arm(data.get('value', False))"),
        ('toggle_record', "self.system.toggle_record(data.get('value', False))"),
        ('toggle_mute', "self.system.toggle_mute(data.get('value', False))"),
        ('set_confidence', "self.system.set_confidence(data.get('value', 0.25))"),
        ('set_model', "self.system.set_model(data.get('value', 'yolov8n.pt'))"),
        ('toggle_skeleton', "self.system.toggle_skeleton(data.get('value', False))"),
        ('toggle_face', "self.system.enable_face = data.get('value', True)"),
        ('toggle_motion', "self.system.enable_motion = data.get('value', True)"),
        ('toggle_heatmap', "self.system.enable_heatmap = data.get('value', False)"),
        ('toggle_night_vision', "self.system.night_vision = data.get('value', False)"),
        ('create_zone', "self.system.create_zone()"),
        ('clear_zones', "self.system.clear_zones()"),
        ('reload_faces', "self.system.reload_faces()")
    ]
    
    broadcast_added = 0
    for cmd_name, line_pattern in commands_to_broadcast:
        # Check if line exists and doesn't have broadcast after it
        if line_pattern in content:
            # Look for the line and check next line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line_pattern in line and i < len(lines) - 1:
                    next_line = lines[i + 1].strip()
                    if not next_line.startswith('await self.broadcast_status()') and next_line != '':
                        # Add broadcast after this line
                        lines.insert(i + 1, '            await self.broadcast_status()')
                        broadcast_added += 1
                        break
            
            content = '\n'.join(lines)
    
    print(f"✓ Added broadcast_status() to {broadcast_added} commands")
    
    # Write patched content
    with open('web_server.py', 'w') as f:
        f.write(content)
    
    print("\n✅ Patch applied successfully!")
    print("Review changes and commit if correct.")

if __name__ == '__main__':
    patch_web_server()
