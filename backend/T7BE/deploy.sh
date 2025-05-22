#!/bin/bash
set -e  # 遇到错误立即退出

# 设置变量
DOCKER_USERNAME="yongchunl"  # 请替换为你的Docker Hub用户名
IMAGE_NAME="t7be"
TAG="latest"
NAMESPACE="default"
FULL_IMAGE_NAME="${DOCKER_USERNAME}/${IMAGE_NAME}:${TAG}"

echo "=== 开始部署 T7BE 应用 ==="

# 登录 Docker Hub (可能需要输入密码)
echo "==> 登录 Docker Hub..."
if docker login; then
  echo "==> Docker Hub登录成功"
else
  echo "!!! Docker Hub登录失败，请检查凭据并重试"
  exit 1
fi

# 构建Docker镜像
echo "==> 构建Docker镜像 ${FULL_IMAGE_NAME}..."
if docker build -t ${FULL_IMAGE_NAME} .; then
  echo "==> 镜像构建成功"
else
  echo "!!! 镜像构建失败，请检查错误并重试"
  exit 1
fi

# 推送镜像到Docker Hub
echo "==> 推送镜像到Docker Hub..."
if docker push ${FULL_IMAGE_NAME}; then
  echo "==> 镜像推送成功"
else
  echo "!!! 镜像推送失败，请检查错误并重试"
  exit 1
fi

# 用远程镜像更新k8s部署文件
echo "==> 更新部署文件中的镜像名称..."
sed -i "s|image: t7be:latest|image: ${FULL_IMAGE_NAME}|g" k8s-deployment.yaml
sed -i "s|imagePullPolicy: IfNotPresent|imagePullPolicy: Always|g" k8s-deployment.yaml

# 应用Kubernetes部署
echo "==> 部署应用到Kubernetes集群..."
kubectl apply -f k8s-deployment.yaml -n ${NAMESPACE}

# 强制滚动更新以应用新镜像
echo "==> 强制执行滚动更新..."
kubectl rollout restart deployment/t7be-deployment -n ${NAMESPACE}

# 检查部署状态
echo "==> 等待部署完成..."
if kubectl rollout status deployment/t7be-deployment -n ${NAMESPACE}; then
  echo "==> 部署状态检查成功"
  
  echo "==> 获取服务访问信息..."
  NODE_PORT=$(kubectl get service t7be-service -n ${NAMESPACE} -o jsonpath='{.spec.ports[0].nodePort}')
  NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' | awk '{print $1}')
  
  echo ""
  echo "=== 部署完成 ==="
  echo "应用可通过以下地址访问: http://${NODE_IP}:${NODE_PORT}"
  echo ""
  echo "服务信息:"
  kubectl get svc t7be-service -n ${NAMESPACE}
  echo ""
  echo "Pod信息:"
  kubectl get pods -l app=t7be -n ${NAMESPACE}
else
  echo "!!! 部署过程出现问题，请检查上面的日志信息"
  exit 1
fi 