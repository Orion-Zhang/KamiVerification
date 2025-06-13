/**
 * 状态切换功能
 * 用于API密钥和卡密的状态切换
 */

class StatusToggle {
    constructor() {
        this.init();
    }

    init() {
        // 绑定状态切换按钮事件
        document.addEventListener('click', (e) => {
            if (e.target.matches('.status-toggle-btn') || e.target.closest('.status-toggle-btn')) {
                e.preventDefault();
                this.handleToggle(e.target.closest('.status-toggle-btn'));
            }
        });

        // 绑定批量操作
        document.addEventListener('change', (e) => {
            if (e.target.matches('.batch-select-all')) {
                this.handleBatchSelectAll(e.target);
            }
        });

        // 绑定批量状态切换
        document.addEventListener('click', (e) => {
            if (e.target.matches('.batch-toggle-btn')) {
                e.preventDefault();
                this.handleBatchToggle(e.target);
            }
        });
    }

    /**
     * 处理单个状态切换
     */
    async handleToggle(button) {
        const itemId = button.dataset.itemId;
        const itemType = button.dataset.itemType; // 'api_key' 或 'card'
        const currentStatus = button.dataset.currentStatus === 'true';
        const actionText = currentStatus ? '禁用' : '启用';

        // 显示确认对话框
        const confirmed = await this.showConfirmDialog(
            `确认${actionText}`,
            `您确定要${actionText}这个${itemType === 'api_key' ? 'API密钥' : '卡密'}吗？`,
            actionText
        );

        if (!confirmed) {
            return;
        }

        // 显示加载状态
        this.setButtonLoading(button, true);

        try {
            // 发送请求
            const url = this.getToggleUrl(itemType, itemId);
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                // 更新按钮状态
                this.updateButtonStatus(button, result.new_status, result.status_text);
                
                // 显示成功消息
                this.showToast('success', result.message);
                
                // 更新表格行样式
                this.updateRowStyle(button, result.new_status);
            } else {
                this.showToast('error', result.message || '操作失败');
            }
        } catch (error) {
            console.error('状态切换失败:', error);
            this.showToast('error', '网络错误，请重试');
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    /**
     * 处理批量选择
     */
    handleBatchSelectAll(checkbox) {
        const table = checkbox.closest('table');
        const itemCheckboxes = table.querySelectorAll('.batch-select-item');
        
        itemCheckboxes.forEach(cb => {
            cb.checked = checkbox.checked;
        });

        this.updateBatchButtons();
    }

    /**
     * 处理批量状态切换
     */
    async handleBatchToggle(button) {
        const action = button.dataset.action; // 'enable' 或 'disable'
        const itemType = button.dataset.itemType;
        const selectedItems = this.getSelectedItems();

        if (selectedItems.length === 0) {
            this.showToast('warning', '请先选择要操作的项目');
            return;
        }

        const actionText = action === 'enable' ? '启用' : '禁用';
        const confirmed = await this.showConfirmDialog(
            `批量${actionText}`,
            `您确定要${actionText} ${selectedItems.length} 个${itemType === 'api_key' ? 'API密钥' : '卡密'}吗？`,
            actionText
        );

        if (!confirmed) {
            return;
        }

        // 显示加载状态
        this.setButtonLoading(button, true);

        try {
            const promises = selectedItems.map(itemId => {
                const url = this.getToggleUrl(itemType, itemId);
                return fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    }
                });
            });

            const responses = await Promise.all(promises);
            const results = await Promise.all(responses.map(r => r.json()));

            let successCount = 0;
            let failCount = 0;

            results.forEach((result, index) => {
                if (result.success) {
                    successCount++;
                    // 更新对应的按钮状态
                    const itemId = selectedItems[index];
                    const toggleButton = document.querySelector(`[data-item-id="${itemId}"].status-toggle-btn`);
                    if (toggleButton) {
                        this.updateButtonStatus(toggleButton, result.new_status, result.status_text);
                        this.updateRowStyle(toggleButton, result.new_status);
                    }
                } else {
                    failCount++;
                }
            });

            if (successCount > 0) {
                this.showToast('success', `成功${actionText} ${successCount} 个项目`);
            }
            if (failCount > 0) {
                this.showToast('warning', `${failCount} 个项目操作失败`);
            }

            // 清除选择
            this.clearSelection();

        } catch (error) {
            console.error('批量操作失败:', error);
            this.showToast('error', '网络错误，请重试');
        } finally {
            this.setButtonLoading(button, false);
        }
    }

    /**
     * 获取切换URL
     */
    getToggleUrl(itemType, itemId) {
        if (itemType === 'api_key') {
            return `/api/keys/${itemId}/toggle-status/`;
        } else if (itemType === 'card') {
            return `/cards/${itemId}/toggle-status/`;
        }
        throw new Error('未知的项目类型');
    }

    /**
     * 更新按钮状态
     */
    updateButtonStatus(button, newStatus, statusText) {
        button.dataset.currentStatus = newStatus;
        
        const icon = button.querySelector('i');
        const text = button.querySelector('.btn-text');
        
        if (newStatus) {
            // 启用状态
            button.className = 'btn btn-success btn-sm status-toggle-btn';
            if (icon) icon.className = 'fas fa-toggle-on me-1';
            if (text) text.textContent = statusText || '启用';
        } else {
            // 禁用状态
            button.className = 'btn btn-secondary btn-sm status-toggle-btn';
            if (icon) icon.className = 'fas fa-toggle-off me-1';
            if (text) text.textContent = statusText || '禁用';
        }
    }

    /**
     * 更新表格行样式
     */
    updateRowStyle(button, newStatus) {
        const row = button.closest('tr');
        if (row) {
            if (newStatus) {
                row.classList.remove('table-secondary');
                row.style.opacity = '1';
            } else {
                row.classList.add('table-secondary');
                row.style.opacity = '0.6';
            }
        }
    }

    /**
     * 设置按钮加载状态
     */
    setButtonLoading(button, loading) {
        const icon = button.querySelector('i');
        const text = button.querySelector('.btn-text');
        
        if (loading) {
            button.disabled = true;
            if (icon) icon.className = 'fas fa-spinner fa-spin me-1';
            if (text) text.textContent = '处理中...';
        } else {
            button.disabled = false;
            // 状态会在updateButtonStatus中更新
        }
    }

    /**
     * 获取选中的项目ID
     */
    getSelectedItems() {
        const checkboxes = document.querySelectorAll('.batch-select-item:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    /**
     * 清除选择
     */
    clearSelection() {
        const checkboxes = document.querySelectorAll('.batch-select-item, .batch-select-all');
        checkboxes.forEach(cb => cb.checked = false);
        this.updateBatchButtons();
    }

    /**
     * 更新批量操作按钮状态
     */
    updateBatchButtons() {
        const selectedCount = this.getSelectedItems().length;
        const batchButtons = document.querySelectorAll('.batch-toggle-btn');
        
        batchButtons.forEach(btn => {
            btn.disabled = selectedCount === 0;
            const countSpan = btn.querySelector('.selected-count');
            if (countSpan) {
                countSpan.textContent = selectedCount;
            }
        });
    }

    /**
     * 显示确认对话框
     */
    showConfirmDialog(title, message, confirmText = '确认') {
        return new Promise((resolve) => {
            // 使用Bootstrap Modal或自定义对话框
            if (typeof bootstrap !== 'undefined') {
                // 创建Bootstrap模态框
                const modalHtml = `
                    <div class="modal fade" id="confirmModal" tabindex="-1">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title">${title}</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body">
                                    <p>${message}</p>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                                    <button type="button" class="btn btn-primary" id="confirmBtn">${confirmText}</button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // 移除现有模态框
                const existingModal = document.getElementById('confirmModal');
                if (existingModal) {
                    existingModal.remove();
                }
                
                // 添加新模态框
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
                
                // 绑定确认按钮事件
                document.getElementById('confirmBtn').addEventListener('click', () => {
                    modal.hide();
                    resolve(true);
                });
                
                // 绑定取消事件
                document.getElementById('confirmModal').addEventListener('hidden.bs.modal', () => {
                    document.getElementById('confirmModal').remove();
                    resolve(false);
                });
                
                modal.show();
            } else {
                // 降级到原生confirm
                resolve(confirm(`${title}\n\n${message}`));
            }
        });
    }

    /**
     * 显示提示消息
     */
    showToast(type, message) {
        // 使用Bootstrap Toast或自定义提示
        if (typeof bootstrap !== 'undefined') {
            const toastHtml = `
                <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'warning'} border-0" role="alert">
                    <div class="d-flex">
                        <div class="toast-body">
                            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'exclamation-triangle'} me-2"></i>
                            ${message}
                        </div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                    </div>
                </div>
            `;
            
            // 创建toast容器（如果不存在）
            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
                toastContainer.style.zIndex = '9999';
                document.body.appendChild(toastContainer);
            }
            
            // 添加toast
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);
            const toastElement = toastContainer.lastElementChild;
            const toast = new bootstrap.Toast(toastElement);
            
            // 显示toast
            toast.show();
            
            // 自动移除
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });
        } else {
            // 降级到alert
            alert(message);
        }
    }

    /**
     * 获取CSRF Token
     */
    getCSRFToken() {
        // 首先尝试从meta标签获取
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }

        // 降级到表单中的token
        const formToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return formToken ? formToken.value : '';
    }
}

// 初始化状态切换功能
document.addEventListener('DOMContentLoaded', () => {
    new StatusToggle();
});
