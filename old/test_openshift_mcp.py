#!/usr/bin/env python3
"""
Test script for OpenShift MCP Server

This script provides a simple way to test the OpenShift MCP server functionality
without needing to set up a full MCP client.
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openshift_cluster import OpenShiftCluster


def test_cluster_connection():
    """Test basic cluster connection."""
    print("Testing OpenShift cluster connection...")
    
    # Load environment variables
    load_dotenv()
    
    cluster_url = os.getenv("OPENSHIFT_CLUSTER_URL")
    token = os.getenv("OPENSHIFT_TOKEN")
    
    if not cluster_url or not token:
        print("Error: Please set OPENSHIFT_CLUSTER_URL and OPENSHIFT_TOKEN in your .env file")
        print("You can copy env.example to .env and fill in your values")
        print("Optional: Set OPENSHIFT_VERIFY_SSL=false for self-signed certificates")
        return False
    
    try:
        # Get SSL verification setting from environment
        verify_ssl = os.getenv("OPENSHIFT_VERIFY_SSL", "true").lower() == "true"
        cluster = OpenShiftCluster(cluster_url, token, verify_ssl)
        print(f"✅ Successfully connected to cluster: {cluster_url} (SSL verify: {verify_ssl})")
        return cluster
    except Exception as e:
        print(f"❌ Failed to connect to cluster: {e}")
        return False


def test_list_namespaces(cluster):
    """Test listing namespaces."""
    print("\nTesting namespace listing...")
    
    try:
        namespaces = cluster.list_namespaces()
        if namespaces:
            print(f"✅ Found {len(namespaces)} namespaces:")
            for ns in namespaces[:5]:  # Show first 5
                print(f"  - {ns['name']} ({ns['display_name']}) - {ns['status']}")
            if len(namespaces) > 5:
                print(f"  ... and {len(namespaces) - 5} more")
        else:
            print("⚠️  No namespaces found")
        return namespaces
    except Exception as e:
        print(f"❌ Error listing namespaces: {e}")
        return []


def test_list_applications(cluster, namespace):
    """Test listing applications in a namespace."""
    print(f"\nTesting application listing in namespace '{namespace}'...")
    
    try:
        applications = cluster.list_applications(namespace)
        if applications:
            print(f"✅ Found {len(applications)} applications:")
            for app in applications:
                print(f"  - {app['name']} ({app['type']}) - {app['image']}")
        else:
            print("⚠️  No applications found")
        return applications
    except Exception as e:
        print(f"❌ Error listing applications: {e}")
        return []


def test_list_pods(cluster, namespace):
    """Test listing pods in a namespace."""
    print(f"\nTesting pod listing in namespace '{namespace}'...")
    
    try:
        pods = cluster.list_pods(namespace)
        if pods:
            print(f"✅ Found {len(pods)} pods:")
            for pod in pods[:3]:  # Show first 3
                print(f"  - {pod['name']} - {pod['status']} - Ready: {pod['ready']}")
            if len(pods) > 3:
                print(f"  ... and {len(pods) - 3} more")
        else:
            print("⚠️  No pods found")
        return pods
    except Exception as e:
        print(f"❌ Error listing pods: {e}")
        return []


def test_list_services(cluster, namespace):
    """Test listing services in a namespace."""
    print(f"\nTesting service listing in namespace '{namespace}'...")
    
    try:
        services = cluster.list_services(namespace)
        if services:
            print(f"✅ Found {len(services)} services:")
            for service in services:
                print(f"  - {service['name']} ({service['type']}) - {service['cluster_ip']}")
        else:
            print("⚠️  No services found")
        return services
    except Exception as e:
        print(f"❌ Error listing services: {e}")
        return []


def test_namespace_info(cluster, namespace):
    """Test getting detailed namespace information."""
    print(f"\nTesting namespace info for '{namespace}'...")
    
    try:
        info = cluster.get_namespace_info(namespace)
        if "error" not in info:
            print(f"✅ Namespace info retrieved:")
            print(f"  - Name: {info['name']}")
            print(f"  - Display Name: {info['display_name']}")
            print(f"  - Status: {info['status']}")
            print(f"  - Resource Quotas: {len(info['resource_quotas'])}")
            print(f"  - Limit Ranges: {len(info['limit_ranges'])}")
        else:
            print(f"❌ Error getting namespace info: {info['error']}")
        return info
    except Exception as e:
        print(f"❌ Error getting namespace info: {e}")
        return {"error": str(e)}


def main():
    """Main test function."""
    print("🚀 OpenShift MCP Server Test")
    print("=" * 50)
    
    # Test cluster connection
    cluster = test_cluster_connection()
    if not cluster:
        return
    
    # Test listing namespaces
    namespaces = test_list_namespaces(cluster)
    if not namespaces:
        print("\n⚠️  Cannot proceed with further tests without namespaces")
        return
    
    # Use the first namespace for further tests
    test_namespace = namespaces[0]['name']
    print(f"\n📋 Using namespace '{test_namespace}' for further tests")
    
    # Test various operations
    test_list_applications(cluster, test_namespace)
    test_list_pods(cluster, test_namespace)
    test_list_services(cluster, test_namespace)
    test_namespace_info(cluster, test_namespace)
    
    print("\n✅ All tests completed!")
    print("\nTo use this with an MCP client, run:")
    print("python openshift_mcp_server.py")


if __name__ == "__main__":
    main() 