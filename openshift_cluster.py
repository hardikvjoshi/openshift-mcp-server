"""
OpenShift Cluster Management Class

This module provides the OpenShiftCluster class for managing OpenShift cluster connections
and operations including namespace listing, application discovery, and administrative tasks.
"""

import logging
from typing import Any, Dict, List, Optional
import datetime

from kubernetes import client
from openshift.dynamic import DynamicClient

logger = logging.getLogger(__name__)


class OpenShiftCluster:
    """OpenShift cluster connection and management class."""
    
    def __init__(self, cluster_url: str, token: str):
        self.cluster_url = cluster_url
        self.token = token
        self.dynamic_client = None
        self.k8s_client = None
        self._connect()
    
    def _connect(self):
        """Establish connection to the OpenShift cluster."""
        try:
            # Configure Kubernetes client
            configuration = client.Configuration()
            configuration.host = self.cluster_url
            configuration.api_key = {"authorization": f"Bearer {self.token}"}
            configuration.verify_ssl = False  # For development - enable SSL verification in production
            
            # Create dynamic client for OpenShift resources
            k8s_client = client.ApiClient(configuration)
            self.dynamic_client = DynamicClient(k8s_client)
            self.k8s_client = k8s_client
            
            logger.info(f"Successfully connected to OpenShift cluster: {self.cluster_url}")
        except Exception as e:
            logger.error(f"Failed to connect to OpenShift cluster: {e}")
            raise
    
    def list_namespaces(self) -> List[Dict[str, Any]]:
        """List all namespaces/projects in the cluster."""
        try:
            v1_projects = self.dynamic_client.resources.get(api_version='project.openshift.io/v1', kind='Project')
            projects = v1_projects.get()
            
            namespaces = []
            for project in projects.items:
                namespace_info = {
                    'name': project.metadata.name,
                    'display_name': project.metadata.annotations.get('openshift.io/display-name', project.metadata.name),
                    'description': project.metadata.annotations.get('openshift.io/description', ''),
                    'status': project.status.phase,
                    'created': project.metadata.creationTimestamp,
                    'labels': project.metadata.labels or {},
                    'annotations': project.metadata.annotations or {}
                }
                namespaces.append(namespace_info)
            
            return namespaces
        except Exception as e:
            logger.error(f"Error listing namespaces: {e}")
            return []
    
    def list_applications(self, namespace: str) -> List[Dict[str, Any]]:
        """List applications running in a specific namespace."""
        try:
            applications = []
            
            # Get Deployments
            v1_deployments = self.dynamic_client.resources.get(api_version='apps/v1', kind='Deployment')
            deployments = v1_deployments.get(namespace=namespace)
            
            for deployment in deployments.items:
                app_info = {
                    'name': deployment.metadata.name,
                    'type': 'Deployment',
                    'replicas': deployment.spec.replicas,
                    'available_replicas': deployment.status.availableReplicas,
                    'ready_replicas': deployment.status.readyReplicas,
                    'labels': deployment.metadata.labels or {},
                    'created': deployment.metadata.creationTimestamp,
                    'image': deployment.spec.template.spec.containers[0].image if deployment.spec.template.spec.containers else 'N/A'
                }
                applications.append(app_info)
            
            # Get StatefulSets
            v1_statefulsets = self.dynamic_client.resources.get(api_version='apps/v1', kind='StatefulSet')
            statefulsets = v1_statefulsets.get(namespace=namespace)
            
            for statefulset in statefulsets.items:
                app_info = {
                    'name': statefulset.metadata.name,
                    'type': 'StatefulSet',
                    'replicas': statefulset.spec.replicas,
                    'ready_replicas': statefulset.status.readyReplicas,
                    'labels': statefulset.metadata.labels or {},
                    'created': statefulset.metadata.creationTimestamp,
                    'image': statefulset.spec.template.spec.containers[0].image if statefulset.spec.template.spec.containers else 'N/A'
                }
                applications.append(app_info)
            
            # Get DaemonSets
            v1_daemonsets = self.dynamic_client.resources.get(api_version='apps/v1', kind='DaemonSet')
            daemonsets = v1_daemonsets.get(namespace=namespace)
            
            for daemonset in daemonsets.items:
                app_info = {
                    'name': daemonset.metadata.name,
                    'type': 'DaemonSet',
                    'desired_number_scheduled': daemonset.status.desiredNumberScheduled,
                    'number_ready': daemonset.status.numberReady,
                    'labels': daemonset.metadata.labels or {},
                    'created': daemonset.metadata.creationTimestamp,
                    'image': daemonset.spec.template.spec.containers[0].image if daemonset.spec.template.spec.containers else 'N/A'
                }
                applications.append(app_info)
            
            return applications
        except Exception as e:
            logger.error(f"Error listing applications in namespace {namespace}: {e}")
            return []
    
    def list_pods(self, namespace: str) -> List[Dict[str, Any]]:
        """List all pods in a namespace."""
        try:
            v1_pods = self.dynamic_client.resources.get(api_version='v1', kind='Pod')
            pods = v1_pods.get(namespace=namespace)
            
            pod_list = []
            for pod in pods.items:
                pod_info = {
                    'name': pod.metadata.name,
                    'status': pod.status.phase,
                    'ready': pod.status.containerStatuses[0].ready if pod.status.containerStatuses else False,
                    'restart_count': pod.status.containerStatuses[0].restartCount if pod.status.containerStatuses else 0,
                    'node': pod.spec.nodeName,
                    'labels': pod.metadata.labels or {},
                    'created': pod.metadata.creationTimestamp,
                    'image': pod.spec.containers[0].image if pod.spec.containers else 'N/A'
                }
                pod_list.append(pod_info)
            
            return pod_list
        except Exception as e:
            logger.error(f"Error listing pods in namespace {namespace}: {e}")
            return []
    
    def list_services(self, namespace: str) -> List[Dict[str, Any]]:
        """List all services in a namespace."""
        try:
            v1_services = self.dynamic_client.resources.get(api_version='v1', kind='Service')
            services = v1_services.get(namespace=namespace)
            
            service_list = []
            for service in services.items:
                service_info = {
                    'name': service.metadata.name,
                    'type': service.spec.type,
                    'cluster_ip': service.spec.clusterIP,
                    'external_ips': service.spec.externalIPs or [],
                    'ports': [{'port': port.port, 'target_port': port.targetPort, 'protocol': port.protocol} for port in service.spec.ports] if service.spec.ports else [],
                    'labels': service.metadata.labels or {},
                    'created': service.metadata.creationTimestamp
                }
                service_list.append(service_info)
            
            return service_list
        except Exception as e:
            logger.error(f"Error listing services in namespace {namespace}: {e}")
            return []
    
    def get_pod_logs(self, namespace: str, pod_name: str, tail_lines: int = 100) -> str:
        """Get logs from a specific pod."""
        try:
            v1_pods = self.dynamic_client.resources.get(api_version='v1', kind='Pod')
            logs = v1_pods.log(name=pod_name, namespace=namespace, tail_lines=tail_lines)
            return logs
        except Exception as e:
            logger.error(f"Error getting logs for pod {pod_name} in namespace {namespace}: {e}")
            return f"Error retrieving logs: {e}"
    
    def describe_resource(self, namespace: str, resource_type: str, resource_name: str) -> Dict[str, Any]:
        """Describe a specific resource."""
        try:
            resource = self.dynamic_client.resources.get(api_version='v1', kind=resource_type)
            result = resource.get(name=resource_name, namespace=namespace)
            return result.to_dict()
        except Exception as e:
            logger.error(f"Error describing resource {resource_name} of type {resource_type} in namespace {namespace}: {e}")
            return {"error": str(e)}
    
    def get_namespace_info(self, namespace: str) -> Dict[str, Any]:
        """Get detailed information about a namespace."""
        try:
            v1_projects = self.dynamic_client.resources.get(api_version='project.openshift.io/v1', kind='Project')
            project = v1_projects.get(name=namespace)
            
            # Get resource quotas
            v1_quotas = self.dynamic_client.resources.get(api_version='v1', kind='ResourceQuota')
            quotas = v1_quotas.get(namespace=namespace)
            
            # Get limit ranges
            v1_limits = self.dynamic_client.resources.get(api_version='v1', kind='LimitRange')
            limits = v1_limits.get(namespace=namespace)
            
            namespace_info = {
                'name': project.metadata.name,
                'display_name': project.metadata.annotations.get('openshift.io/display-name', project.metadata.name),
                'description': project.metadata.annotations.get('openshift.io/description', ''),
                'status': project.status.phase,
                'created': project.metadata.creationTimestamp,
                'labels': project.metadata.labels or {},
                'annotations': project.metadata.annotations or {},
                'resource_quotas': [quota.to_dict() for quota in quotas.items],
                'limit_ranges': [limit.to_dict() for limit in limits.items]
            }
            
            return namespace_info
        except Exception as e:
            logger.error(f"Error getting namespace info for {namespace}: {e}")
            return {"error": str(e)}
    
    def list_routes(self, namespace: str) -> List[Dict[str, Any]]:
        """List all routes in a namespace."""
        try:
            v1_routes = self.dynamic_client.resources.get(api_version='route.openshift.io/v1', kind='Route')
            routes = v1_routes.get(namespace=namespace)
            
            route_list = []
            for route in routes.items:
                route_info = {
                    'name': route.metadata.name,
                    'host': route.spec.host,
                    'service_name': route.spec.to.name,
                    'port': route.spec.port.targetPort if route.spec.port else None,
                    'tls': route.spec.tls is not None,
                    'labels': route.metadata.labels or {},
                    'created': route.metadata.creationTimestamp
                }
                route_list.append(route_info)
            
            return route_list
        except Exception as e:
            logger.error(f"Error listing routes in namespace {namespace}: {e}")
            return []
    
    def list_configmaps(self, namespace: str) -> List[Dict[str, Any]]:
        """List all configmaps in a namespace."""
        try:
            v1_configmaps = self.dynamic_client.resources.get(api_version='v1', kind='ConfigMap')
            configmaps = v1_configmaps.get(namespace=namespace)
            
            configmap_list = []
            for configmap in configmaps.items:
                configmap_info = {
                    'name': configmap.metadata.name,
                    'data_keys': list(configmap.data.keys()) if configmap.data else [],
                    'labels': configmap.metadata.labels or {},
                    'created': configmap.metadata.creationTimestamp
                }
                configmap_list.append(configmap_info)
            
            return configmap_list
        except Exception as e:
            logger.error(f"Error listing configmaps in namespace {namespace}: {e}")
            return []
    
    def list_secrets(self, namespace: str) -> List[Dict[str, Any]]:
        """List all secrets in a namespace."""
        try:
            v1_secrets = self.dynamic_client.resources.get(api_version='v1', kind='Secret')
            secrets = v1_secrets.get(namespace=namespace)
            
            secret_list = []
            for secret in secrets.items:
                secret_info = {
                    'name': secret.metadata.name,
                    'type': secret.type,
                    'data_keys': list(secret.data.keys()) if secret.data else [],
                    'labels': secret.metadata.labels or {},
                    'created': secret.metadata.creationTimestamp
                }
                secret_list.append(secret_info)
            
            return secret_list
        except Exception as e:
            logger.error(f"Error listing secrets in namespace {namespace}: {e}")
            return []
    
    def scale_deployment(self, namespace: str, deployment_name: str, replicas: int) -> Dict[str, Any]:
        """Scale a deployment to the specified number of replicas."""
        try:
            v1_deployments = self.dynamic_client.resources.get(api_version='apps/v1', kind='Deployment')
            deployment = v1_deployments.get(name=deployment_name, namespace=namespace)
            
            # Update the replica count
            deployment.spec.replicas = replicas
            updated_deployment = v1_deployments.replace(deployment)
            
            return {
                'success': True,
                'message': f'Successfully scaled deployment {deployment_name} to {replicas} replicas',
                'name': updated_deployment.metadata.name,
                'replicas': updated_deployment.spec.replicas
            }
        except Exception as e:
            logger.error(f"Error scaling deployment {deployment_name} in namespace {namespace}: {e}")
            return {'success': False, 'error': str(e)}
    
    def restart_deployment(self, namespace: str, deployment_name: str) -> Dict[str, Any]:
        """Restart a deployment by patching it with a restart annotation."""
        try:
            v1_deployments = self.dynamic_client.resources.get(api_version='apps/v1', kind='Deployment')
            
            # Add restart annotation to trigger rollout
            patch = {
                'spec': {
                    'template': {
                        'metadata': {
                            'annotations': {
                                'kubectl.kubernetes.io/restartedAt': str(datetime.datetime.now().isoformat())
                            }
                        }
                    }
                }
            }
            
            updated_deployment = v1_deployments.patch(
                name=deployment_name,
                namespace=namespace,
                body=patch
            )
            
            return {
                'success': True,
                'message': f'Successfully restarted deployment {deployment_name}',
                'name': updated_deployment.metadata.name
            }
        except Exception as e:
            logger.error(f"Error restarting deployment {deployment_name} in namespace {namespace}: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_cluster_health(self) -> Dict[str, Any]:
        """Get overall cluster health information."""
        try:
            health_info = {
                'nodes': [],
                'namespaces_count': 0,
                'total_pods': 0,
                'running_pods': 0,
                'failed_pods': 0,
                'pending_pods': 0
            }
            
            # Get nodes
            v1_nodes = self.dynamic_client.resources.get(api_version='v1', kind='Node')
            nodes = v1_nodes.get()
            
            for node in nodes.items:
                node_info = {
                    'name': node.metadata.name,
                    'status': node.status.conditions[-1].type if node.status.conditions else 'Unknown',
                    'ready': any(cond.type == 'Ready' and cond.status == 'True' for cond in node.status.conditions),
                    'capacity': {
                        'cpu': node.status.capacity.get('cpu', 'N/A'),
                        'memory': node.status.capacity.get('memory', 'N/A')
                    }
                }
                health_info['nodes'].append(node_info)
            
            # Get namespaces count
            v1_projects = self.dynamic_client.resources.get(api_version='project.openshift.io/v1', kind='Project')
            projects = v1_projects.get()
            health_info['namespaces_count'] = len(projects.items)
            
            # Get pods across all namespaces
            v1_pods = self.dynamic_client.resources.get(api_version='v1', kind='Pod')
            pods = v1_pods.get()
            
            for pod in pods.items:
                health_info['total_pods'] += 1
                if pod.status.phase == 'Running':
                    health_info['running_pods'] += 1
                elif pod.status.phase == 'Failed':
                    health_info['failed_pods'] += 1
                elif pod.status.phase == 'Pending':
                    health_info['pending_pods'] += 1
            
            return health_info
        except Exception as e:
            logger.error(f"Error getting cluster health: {e}")
            return {'error': str(e)}
    
    def get_resource_usage(self, namespace: str) -> Dict[str, Any]:
        """Get resource usage information for a namespace."""
        try:
            usage_info = {
                'namespace': namespace,
                'pods': [],
                'total_cpu_request': 0,
                'total_memory_request': 0,
                'total_cpu_limit': 0,
                'total_memory_limit': 0
            }
            
            # Get pods in namespace
            v1_pods = self.dynamic_client.resources.get(api_version='v1', kind='Pod')
            pods = v1_pods.get(namespace=namespace)
            
            for pod in pods.items:
                pod_usage = {
                    'name': pod.metadata.name,
                    'status': pod.status.phase,
                    'cpu_request': 0,
                    'memory_request': 0,
                    'cpu_limit': 0,
                    'memory_limit': 0
                }
                
                # Calculate resource requests and limits
                for container in pod.spec.containers:
                    if container.resources.requests:
                        if 'cpu' in container.resources.requests:
                            cpu_req = self._parse_cpu_value(container.resources.requests['cpu'])
                            pod_usage['cpu_request'] += cpu_req
                            usage_info['total_cpu_request'] += cpu_req
                        
                        if 'memory' in container.resources.requests:
                            mem_req = self._parse_memory_value(container.resources.requests['memory'])
                            pod_usage['memory_request'] += mem_req
                            usage_info['total_memory_request'] += mem_req
                    
                    if container.resources.limits:
                        if 'cpu' in container.resources.limits:
                            cpu_limit = self._parse_cpu_value(container.resources.limits['cpu'])
                            pod_usage['cpu_limit'] += cpu_limit
                            usage_info['total_cpu_limit'] += cpu_limit
                        
                        if 'memory' in container.resources.limits:
                            mem_limit = self._parse_memory_value(container.resources.limits['memory'])
                            pod_usage['memory_limit'] += mem_limit
                            usage_info['total_memory_limit'] += mem_limit
                
                usage_info['pods'].append(pod_usage)
            
            return usage_info
        except Exception as e:
            logger.error(f"Error getting resource usage for namespace {namespace}: {e}")
            return {'error': str(e)}
    
    def _parse_cpu_value(self, cpu_str: str) -> float:
        """Parse CPU value from Kubernetes format (e.g., '100m' = 0.1)."""
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000
        return float(cpu_str)
    
    def _parse_memory_value(self, memory_str: str) -> int:
        """Parse memory value from Kubernetes format (e.g., '1Gi' = 1073741824 bytes)."""
        if memory_str.endswith('Ki'):
            return int(memory_str[:-2]) * 1024
        elif memory_str.endswith('Mi'):
            return int(memory_str[:-2]) * 1024 * 1024
        elif memory_str.endswith('Gi'):
            return int(memory_str[:-2]) * 1024 * 1024 * 1024
        elif memory_str.endswith('Ti'):
            return int(memory_str[:-2]) * 1024 * 1024 * 1024 * 1024
        elif memory_str.endswith('K') or memory_str.endswith('k'):
            return int(memory_str[:-1]) * 1000
        elif memory_str.endswith('M'):
            return int(memory_str[:-1]) * 1000 * 1000
        elif memory_str.endswith('G'):
            return int(memory_str[:-1]) * 1000 * 1000 * 1000
        elif memory_str.endswith('T'):
            return int(memory_str[:-1]) * 1000 * 1000 * 1000 * 1000
        else:
            return int(memory_str) 