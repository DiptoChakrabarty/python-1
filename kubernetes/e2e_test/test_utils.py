# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import unittest
import time 
import yaml
from kubernetes import utils, client
from kubernetes.client.rest import ApiException
from kubernetes.e2e_test import base


class TestUtils(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.config = base.get_e2e_configuration()
        cls.path_prefix = "kubernetes/e2e_test/test_yaml/"
        cls.test_namespace = "e2e-test-utils"
        k8s_client = client.api_client.ApiClient(configuration=cls.config)
        core_v1 = client.CoreV1Api(api_client=k8s_client)
        body = client.V1Namespace(metadata=client.V1ObjectMeta(name=cls.test_namespace))
        core_v1.create_namespace(body=body)

    @classmethod
    def tearDownClass(cls):
        k8s_client = client.api_client.ApiClient(configuration=cls.config)
        core_v1 = client.CoreV1Api(api_client=k8s_client)
        core_v1.delete_namespace(name=cls.test_namespace)
    # Tests for creating individual API objects

    def test_create_apps_deployment_from_yaml(self):
        """
        Should be able to create an apps/v1 deployment.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "apps-deployment.yaml")
        app_api = client.AppsV1Api(k8s_client)
        dep = app_api.read_namespaced_deployment(name="nginx-app",
                                                 namespace="default")
        self.assertIsNotNone(dep)
        while True:
            try:
                app_api.delete_namespaced_deployment(
                    name="nginx-app", namespace="default",
                    body={})
                break
            except ApiException:
                continue

    def test_create_apps_deployment_from_yaml_obj(self):
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        with open(self.path_prefix + "apps-deployment.yaml") as f:
            yml_obj = yaml.safe_load(f)

        yml_obj["metadata"]["name"] = "nginx-app-3"
        operation = "create"
        utils.operate_from_dict(k8s_client, yml_obj,operation)

        app_api = client.AppsV1Api(k8s_client)
        dep = app_api.read_namespaced_deployment(name="nginx-app-3",
                                                 namespace="default")
        self.assertIsNotNone(dep)
        app_api.delete_namespaced_deployment(
            name="nginx-app-3", namespace="default",
            body={})

    def test_create_pod_from_yaml(self):
        """
        Should be able to create a pod.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "core-pod.yaml")
        core_api = client.CoreV1Api(k8s_client)
        pod = core_api.read_namespaced_pod(name="myapp-pod",
                                           namespace="default")
        self.assertIsNotNone(pod)
        core_api.delete_namespaced_pod(
            name="myapp-pod", namespace="default",
            body={})

    def test_create_service_from_yaml(self):
        """
        Should be able to create a service.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "core-service.yaml")
        core_api = client.CoreV1Api(k8s_client)
        svc = core_api.read_namespaced_service(name="my-service",
                                               namespace="default")
        self.assertIsNotNone(svc)
        core_api.delete_namespaced_service(
            name="my-service", namespace="default",
            body={})

    def test_create_namespace_from_yaml(self):
        """
        Should be able to create a namespace.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "core-namespace.yaml")
        core_api = client.CoreV1Api(k8s_client)
        nmsp = core_api.read_namespace(name="development")
        self.assertIsNotNone(nmsp)
        core_api.delete_namespace(name="development", body={})

    def test_create_rbac_role_from_yaml(self):
        """
        Should be able to create an rbac role.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "rbac-role.yaml")
        rbac_api = client.RbacAuthorizationV1Api(k8s_client)
        rbac_role = rbac_api.read_namespaced_role(
            name="pod-reader", namespace="default")
        self.assertIsNotNone(rbac_role)
        rbac_api.delete_namespaced_role(
            name="pod-reader", namespace="default", body={})

    def test_create_rbac_role_from_yaml_with_verbose_enabled(self):
        """
        Should be able to create an rbac role with verbose enabled.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "rbac-role.yaml", verbose=True)
        rbac_api = client.RbacAuthorizationV1Api(k8s_client)
        rbac_role = rbac_api.read_namespaced_role(
            name="pod-reader", namespace="default")
        self.assertIsNotNone(rbac_role)
        rbac_api.delete_namespaced_role(
            name="pod-reader", namespace="default", body={})

    def test_create_deployment_non_default_namespace_from_yaml(self):
        """
        Should be able to create a namespace "dep",
        and then create a deployment in the just-created namespace.
        """
        k8s_client = client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "dep-namespace.yaml")
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "dep-deployment.yaml")
        core_api = client.CoreV1Api(k8s_client)
        ext_api = client.AppsV1Api(k8s_client)
        nmsp = core_api.read_namespace(name="dep")
        self.assertIsNotNone(nmsp)
        dep = ext_api.read_namespaced_deployment(name="nginx-deployment",
                                                 namespace="dep")
        self.assertIsNotNone(dep)
        ext_api.delete_namespaced_deployment(
            name="nginx-deployment", namespace="dep",
            body={})
        core_api.delete_namespace(name="dep", body={})

    def test_create_apiservice_from_yaml_with_conflict(self):
        """
        Should be able to create an API service.
        Should verify that creating the same API service should
        fail due to conflict.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "api-service.yaml")
        reg_api = client.ApiregistrationV1beta1Api(k8s_client)
        svc = reg_api.read_api_service(
            name="v1alpha1.wardle.k8s.io")
        self.assertIsNotNone(svc)
        with self.assertRaises(utils.FailToExecuteError) as cm:
            utils.create_from_yaml(
                k8s_client, "kubernetes/e2e_test/test_yaml/api-service.yaml")
        exp_error = ('Error from server (Conflict): '
                     '{"kind":"Status","apiVersion":"v1","metadata":{},'
                     '"status":"Failure",'
                     '"message":"apiservices.apiregistration.k8s.io '
                     '\\"v1alpha1.wardle.k8s.io\\" already exists",'
                     '"reason":"AlreadyExists",'
                     '"details":{"name":"v1alpha1.wardle.k8s.io",'
                     '"group":"apiregistration.k8s.io","kind":"apiservices"},'
                     '"code":409}\n'
                     )
        self.assertEqual(exp_error, str(cm.exception))
        reg_api.delete_api_service(
            name="v1alpha1.wardle.k8s.io", body={})

    # Tests for creating API objects from lists

    def test_create_general_list_from_yaml(self):
        """
        Should be able to create a service and a deployment
        from a kind: List yaml file
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "list.yaml")
        core_api = client.CoreV1Api(k8s_client)
        ext_api = client.AppsV1Api(k8s_client)
        svc = core_api.read_namespaced_service(name="list-service-test",
                                               namespace="default")
        self.assertIsNotNone(svc)
        dep = ext_api.read_namespaced_deployment(name="list-deployment-test",
                                                 namespace="default")
        self.assertIsNotNone(dep)
        core_api.delete_namespaced_service(name="list-service-test",
                                           namespace="default", body={})
        ext_api.delete_namespaced_deployment(name="list-deployment-test",
                                             namespace="default", body={})

    def test_create_namespace_list_from_yaml(self):
        """
        Should be able to create two namespaces
        from a kind: NamespaceList yaml file
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "namespace-list.yaml")
        core_api = client.CoreV1Api(k8s_client)
        nmsp_1 = core_api.read_namespace(name="mock-1")
        self.assertIsNotNone(nmsp_1)
        nmsp_2 = core_api.read_namespace(name="mock-2")
        self.assertIsNotNone(nmsp_2)
        core_api.delete_namespace(name="mock-1", body={})
        core_api.delete_namespace(name="mock-2", body={})

    def test_create_implicit_service_list_from_yaml_with_conflict(self):
        """
        Should be able to create two services from a kind: ServiceList
        json file that implicitly indicates the kind of individual objects
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        with self.assertRaises(utils.FailToExecuteError):
            utils.create_from_yaml(
                k8s_client, self.path_prefix + "implicit-svclist.json")
        core_api = client.CoreV1Api(k8s_client)
        svc_3 = core_api.read_namespaced_service(name="mock-3",
                                                 namespace="default")
        self.assertIsNotNone(svc_3)
        svc_4 = core_api.read_namespaced_service(name="mock-4",
                                                 namespace="default")
        self.assertIsNotNone(svc_4)
        core_api.delete_namespaced_service(name="mock-3",
                                           namespace="default", body={})
        core_api.delete_namespaced_service(name="mock-4",
                                           namespace="default", body={})

    # Tests for multi-resource yaml objects

    def test_create_from_multi_resource_yaml(self):
        """
        Should be able to create a service and a replication controller
        from a multi-resource yaml file
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "multi-resource.yaml")
        core_api = client.CoreV1Api(k8s_client)
        svc = core_api.read_namespaced_service(name="mock",
                                               namespace="default")
        self.assertIsNotNone(svc)
        ctr = core_api.read_namespaced_replication_controller(
            name="mock", namespace="default")
        self.assertIsNotNone(ctr)
        core_api.delete_namespaced_replication_controller(
            name="mock", namespace="default", body={})
        core_api.delete_namespaced_service(name="mock",
                                           namespace="default", body={})

    def test_create_from_list_in_multi_resource_yaml(self):
        """
        Should be able to create the items in the PodList and a deployment
        specified in the multi-resource file
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "multi-resource-with-list.yaml")
        core_api = client.CoreV1Api(k8s_client)
        app_api = client.AppsV1Api(k8s_client)
        pod_0 = core_api.read_namespaced_pod(
            name="mock-pod-0", namespace="default")
        self.assertIsNotNone(pod_0)
        pod_1 = core_api.read_namespaced_pod(
            name="mock-pod-1", namespace="default")
        self.assertIsNotNone(pod_1)
        dep = app_api.read_namespaced_deployment(
            name="mock", namespace="default")
        self.assertIsNotNone(dep)
        core_api.delete_namespaced_pod(
            name="mock-pod-0", namespace="default", body={})
        core_api.delete_namespaced_pod(
            name="mock-pod-1", namespace="default", body={})
        app_api.delete_namespaced_deployment(
            name="mock", namespace="default", body={})

    def test_create_from_multi_resource_yaml_with_conflict(self):
        """
        Should be able to create a service from the first yaml file.
        Should fail to create the same service from the second yaml file
        and create a replication controller.
        Should raise an exception for failure to create the same service twice.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "yaml-conflict-first.yaml")
        core_api = client.CoreV1Api(k8s_client)
        svc = core_api.read_namespaced_service(name="mock-2",
                                               namespace="default")
        self.assertIsNotNone(svc)
        with self.assertRaises(utils.FailToExecuteError) as cm:
            utils.create_from_yaml(
                k8s_client, self.path_prefix + "yaml-conflict-multi.yaml")
        exp_error = ('Error from server (Conflict): {"kind":"Status",'
                     '"apiVersion":"v1","metadata":{},"status":"Failure",'
                     '"message":"services \\"mock-2\\" already exists",'
                     '"reason":"AlreadyExists","details":{"name":"mock-2",'
                     '"kind":"services"},"code":409}\n'
                     )
        self.assertEqual(exp_error, str(cm.exception))
        ctr = core_api.read_namespaced_replication_controller(
            name="mock-2", namespace="default")
        self.assertIsNotNone(ctr)
        core_api.delete_namespaced_replication_controller(
            name="mock-2", namespace="default", body={})
        core_api.delete_namespaced_service(name="mock-2",
                                           namespace="default", body={})

    def test_create_from_multi_resource_yaml_with_multi_conflicts(self):
        """
        Should create an apps/v1 deployment
        and fail to create the same deployment twice.
        Should raise an exception that contains two error messages.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        with self.assertRaises(utils.FailToExecuteError) as cm:
            utils.create_from_yaml(
                k8s_client, self.path_prefix + "triple-nginx.yaml")
        exp_error = ('Error from server (Conflict): {"kind":"Status",'
                     '"apiVersion":"v1","metadata":{},"status":"Failure",'
                     '"message":"deployments.apps \\"triple-nginx\\" '
                     'already exists","reason":"AlreadyExists",'
                     '"details":{"name":"triple-nginx","group":"apps",'
                     '"kind":"deployments"},"code":409}\n'
                     )
        exp_error += exp_error
        self.assertEqual(exp_error, str(cm.exception))
        ext_api = client.AppsV1Api(k8s_client)
        dep = ext_api.read_namespaced_deployment(name="triple-nginx",
                                                 namespace="default")
        self.assertIsNotNone(dep)
        ext_api.delete_namespaced_deployment(
            name="triple-nginx", namespace="default",
            body={})

    def test_create_namespaced_apps_deployment_from_yaml(self):
        """
        Should be able to create an apps/v1beta1 deployment
		in a test namespace.
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "apps-deployment.yaml",
            namespace=self.test_namespace)
        app_api = client.AppsV1Api(k8s_client)
        dep = app_api.read_namespaced_deployment(name="nginx-app",
                                                 namespace=self.test_namespace)
        self.assertIsNotNone(dep)
        app_api.delete_namespaced_deployment(
            name="nginx-app", namespace=self.test_namespace,
            body={})

    def test_create_from_list_in_multi_resource_yaml_namespaced(self):
        """
        Should be able to create the items in the PodList and a deployment
        specified in the multi-resource file in a test namespace
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "multi-resource-with-list.yaml",
            namespace=self.test_namespace)
        core_api = client.CoreV1Api(k8s_client)
        app_api = client.AppsV1Api(k8s_client)
        pod_0 = core_api.read_namespaced_pod(
            name="mock-pod-0", namespace=self.test_namespace)
        self.assertIsNotNone(pod_0)
        pod_1 = core_api.read_namespaced_pod(
            name="mock-pod-1", namespace=self.test_namespace)
        self.assertIsNotNone(pod_1)
        dep = app_api.read_namespaced_deployment(
            name="mock", namespace=self.test_namespace)
        self.assertIsNotNone(dep)
        core_api.delete_namespaced_pod(
            name="mock-pod-0", namespace=self.test_namespace, body={})
        core_api.delete_namespaced_pod(
            name="mock-pod-1", namespace=self.test_namespace, body={})
        app_api.delete_namespaced_deployment(
            name="mock", namespace=self.test_namespace, body={})

    
    def test_delete_apps_deployment_from_yaml(self):
        """
        Should delete a deployment 

        First create deployment from file and ensure it is created
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "apps-deployment.yaml")
        app_api = client.AppsV1Api(k8s_client)
        dep = app_api.read_namespaced_deployment(name="nginx-app",
                                                 namespace="default")
        self.assertIsNotNone(dep)
        """
        Deployment should be created 

        Now delete deployment using delete_from_yaml method
        """
        utils.delete_from_yaml(k8s_client, self.path_prefix + "apps-deployment.yaml")
        deployment_status=False
        try:
            response=app_api.read_namespaced_deployment(name="nginx-app",namespace="default")
            deployment_status=True
        except Exception as e:
            self.assertFalse(deployment_status)

        self.assertFalse(deployment_status)

    def test_delete_service_from_yaml(self):
        """
        Should be able to delete a service

        Create service from yaml first and ensure it is created
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "core-service.yaml")
        core_api = client.CoreV1Api(k8s_client)
        svc = core_api.read_namespaced_service(name="my-service",
                                               namespace="default")
        self.assertIsNotNone(svc)
        """
        Delete service from yaml
        """
        utils.delete_from_yaml(
            k8s_client, self.path_prefix + "core-service.yaml")
        service_status=False
        try:
            response = core_api.read_namespaced_service(name="my-service",namespace="default")
            service_status=True 
        except Exception as e:
            self.assertFalse(service_status)
        self.assertFalse(service_status)

    def test_delete_namespace_from_yaml(self):
        """
        Should be able to delete a namespace
        Create namespace from file first and ensure it is created
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        time.sleep(120)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "core-namespace.yaml")
        core_api = client.CoreV1Api(k8s_client)
        nmsp = core_api.read_namespace(name="development")
        self.assertIsNotNone(nmsp)
        """
        Delete namespace from yaml
        """
        utils.delete_from_yaml(k8s_client, self.path_prefix + "core-namespace.yaml")
        time.sleep(120)
        namespace_status=False
        try:
            response=core_api.read_namespace(name="development")
            namespace_status=True
        except Exception as e:
            self.assertFalse(namespace_status)
        self.assertFalse(namespace_status)

    
    def test_delete_pod_from_yaml(self):
        """
        Should be able to delete pod

        Create pod from file first and ensure it is created
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        time.sleep(120)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "core-pod.yaml")
        core_api = client.CoreV1Api(k8s_client)
        pod = core_api.read_namespaced_pod(name="myapp-pod",
                                            namespace="default")
        self.assertIsNotNone(pod)
        """
        Delete pod using delete_from_yaml
        """
        utils.delete_from_yaml(
            k8s_client, self.path_prefix + "core-pod.yaml")
        time.sleep(120)
        pod_status=False
        try:
            response = core_api.read_namespaced_pod(name="myapp-pod",
                                            namespace="default")
            pod_status=True
        except Exception as e:
            self.assertFalse(pod_status)
        self.assertFalse(pod_status)


    def test_delete_rbac_role_from_yaml(self):
        """
        Should be able to delete rbac role

        Create rbac role from file first and ensure it is created
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "rbac-role.yaml")
        rbac_api = client.RbacAuthorizationV1Api(k8s_client)
        rbac_role = rbac_api.read_namespaced_role(
            name="pod-reader", namespace="default")
        self.assertIsNotNone(rbac_role)
        """
        Delete rbac role from yaml
        """
        utils.delete_from_yaml(
            k8s_client, self.path_prefix + "rbac-role.yaml")
        rbac_role_status=False
        try:
            response = rbac_api.read_namespaced_role(
            name="pod-reader", namespace="default")
            rbac_role_status=True
        except Exception as e:
            self.assertFalse(rbac_role_status)
        self.assertFalse(rbac_role_status)

    def test_delete_rbac_role_from_yaml_with_verbose_enabled(self):
        """
        Should delete a rbac role with verbose enabled

        Create rbac role with verbose enabled and ensure it is created
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "rbac-role.yaml", verbose=True)
        rbac_api = client.RbacAuthorizationV1Api(k8s_client)
        rbac_role = rbac_api.read_namespaced_role(
            name="pod-reader", namespace="default")
        self.assertIsNotNone(rbac_role)
        """
        Delete the rbac role from yaml
        """
        utils.delete_from_yaml(
            k8s_client, self.path_prefix + "rbac-role.yaml", verbose=True)
        
        rbac_role_status=False
        try:
            response=rbac_api.read_namespaced_role(
            name="pod-reader", namespace="default")
            rbac_role_status=True
        except Exception as e:
            self.assertFalse(rbac_role_status)
        self.assertFalse(rbac_role_status)
    

    # Deletion Tests for multi resource objects in yaml files

    def test_delete_from_multi_resource_yaml(self):
        """
        Should be able to delete service and replication controller 
        from the multi resource yaml files

        Create the resources first and ensure they exist
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "multi-resource.yaml")
        core_api = client.CoreV1Api(k8s_client)
        svc = core_api.read_namespaced_service(name="mock",
                                               namespace="default")
        self.assertIsNotNone(svc)
        ctr = core_api.read_namespaced_replication_controller(
            name="mock", namespace="default")
        self.assertIsNotNone(ctr)
        """
        Delete service and replication controller using yaml file
        """
        utils.delete_from_yaml(
            k8s_client, self.path_prefix + "multi-resource.yaml")
        svc_status=False
        replication_status=False
        try:
            resp_svc= core_api.read_namespaced_service(name="mock",
                                               namespace="default")
            svc_status=True
            resp_repl= core_api.read_namespaced_replication_controller(
            name="mock", namespace="default")
            repl_status = True
        except Exception as e:
            self.assertFalse(svc_status)
            self.assertFalse(replication_status)
        self.assertFalse(svc_status)
        self.assertFalse(replication_status)




    
    def test_delete_from_list_in_multi_resource_yaml(self):
        """
        Should delete the items in PodList and the deployment in the yaml file

        Create the items first and ensure they exist
        """
        k8s_client = client.api_client.ApiClient(configuration=self.config)
        time.sleep(120)
        utils.create_from_yaml(
            k8s_client, self.path_prefix + "multi-resource-with-list.yaml")
        core_api = client.CoreV1Api(k8s_client)
        app_api = client.AppsV1Api(k8s_client)
        pod_0 = core_api.read_namespaced_pod(
            name="mock-pod-0", namespace="default")
        self.assertIsNotNone(pod_0)
        pod_1 = core_api.read_namespaced_pod(
            name="mock-pod-1", namespace="default")
        self.assertIsNotNone(pod_1)
        dep = app_api.read_namespaced_deployment(
            name="mock", namespace="default")
        self.assertIsNotNone(dep)
        """
        Delete the PodList and Deployment using the yaml file
        """
        utils.delete_from_yaml(
            k8s_client, self.path_prefix + "multi-resource-with-list.yaml")
        time.sleep(120)
        pod0_status=False
        pod1_status=False
        deploy_status=False
        try:
            core_api.read_namespaced_pod(
            name="mock-pod-0", namespace="default")
            core_api.read_namespaced_pod(
            name="mock-pod-1", namespace="default")
            app_api.read_namespaced_deployment(
            name="mock", namespace="default")
            pod0_status=True
            pod1_status=True
            deploy_status=True
        except Exception as e:
            self.assertFalse(pod0_status)
            self.assertFalse(pod1_status)
            self.assertFalse(deploy_status)
        self.assertFalse(pod0_status)
        self.assertFalse(pod1_status)
        self.assertFalse(deploy_status)




    







