#!/usr/bin/env python3
"""
API Endpoint Verification Script
Tests all critical trading-nexus API endpoints
"""
import requests
import json
import time

# API Base URLs
ENDPOINTS = {
    'health': {
        'url': '/health',
        'method': 'GET',
        'description': 'Health check endpoint',
        'expected': 200
    },
    'health_v2': {
        'url': '/api/v2/health',
        'method': 'GET',
        'description': 'API v2 Health check',
        'expected': 200
    },
    'dhan_status': {
        'url': '/api/v2/admin/dhan/status',
        'method': 'GET',
        'description': 'DhanHQ connection status',
        'expected': 200
    },
    'notifications': {
        'url': '/api/v2/admin/notifications?limit=3',
        'method': 'GET',
        'description': 'Sample notifications',
        'expected': 200
    },
    'market_status': {
        'url': '/api/v2/market/nse-status',
        'method': 'GET',
        'description': 'Market status',
        'expected': 200
    },
}

def test_endpoint(base_url, name, config):
    """Test a single endpoint"""
    url = base_url + config['url']
    try:
        start = time.time()
        resp = requests.get(url, timeout=5)
        elapsed = (time.time() - start) * 1000
        
        status_ok = resp.status_code == config['expected']
        icon = '✓' if status_ok else '✗'
        
        return {
            'name': name,
            'url': config['url'],
            'status': resp.status_code,
            'elapsed': f'{elapsed:.0f}ms',
            'ok': status_ok,
            'icon': icon,
            'description': config['description']
        }
    except requests.exceptions.Timeout:
        return {
            'name': name,
            'url': config['url'],
            'status': 'TIMEOUT',
            'elapsed': '5000ms',
            'ok': False,
            'icon': '✗',
            'description': config['description']
        }
    except requests.exceptions.ConnectionError:
        return {
            'name': name,
            'url': config['url'],
            'status': 'CONN_ERROR',
            'elapsed': '-',
            'ok': False,
            'icon': '✗',
            'description': config['description']
        }
    except Exception as e:
        return {
            'name': name,
            'url': config['url'],
            'status': 'ERROR',
            'elapsed': '-',
            'ok': False,
            'icon': '✗',
            'description': config['description'],
            'error': str(e)[:50]
        }

def main():
    # Try different base URLs
    base_urls = [
        ('72.62.228.112', 'VPS IP (direct)'),
        ('api.tradingnexus.pro', 'Production domain'),
        ('localhost:3000', 'Local dev'),
    ]
    
    print('=' * 80)
    print('TRADING-NEXUS API ENDPOINT VERIFICATION')
    print('=' * 80)
    print()
    
    for base_ip, label in base_urls:
        base_url = f'http://{base_ip}'
        print(f'\n📍 Testing against: {label}')
        print(f'   Base URL: {base_url}')
        print('-' * 80)
        
        results = []
        for name, config in ENDPOINTS.items():
            result = test_endpoint(base_url, name, config)
            results.append(result)
            
            status_str = str(result['status']).rjust(4)
            elapsed_str = result['elapsed'].rjust(7)
            icon = result['icon']
            desc = result['description']
            
            print(f'{icon} {name:15} {status_str}  {elapsed_str}  {desc}')
        
        # Summary
        passed = sum(1 for r in results if r['ok'])
        total = len(results)
        print('-' * 80)
        print(f'Result: {passed}/{total} endpoints responding\n')
        
        if passed > 0:
            print(f'✅ SUCCESS - API is accessible via {label}')
            print(f'   Access your API at: {base_url}/api/v2/...')
            
            if passed == total:
                print(f'✅ ALL ENDPOINTS HEALTHY')
            return True
    
    print()
    print('=' * 80)
    print('⚠️  No endpoints responding yet')
    print()
    print('Possible reasons:')
    print('  1. Traefik routing not fully initialized (wait 30 seconds)')
    print('  2. DNS not configured for api.tradingnexus.pro')
    print('  3. Backend still starting up')
    print()
    print('Diagnostic steps:')
    print('  1. Check Coolify dashboard at: http://72.62.228.112:8000/')
    print('  2. View application logs: Projects → trade-nexuss → trade-nexus-v2 → Logs')
    print('  3. Verify containers are running: Status show "running:healthy"')
    print()
    print('=' * 80)
    return False

if __name__ == '__main__':
    main()
