from rest_framework import status


class ApiErrorCode:
    """API错误码常量类"""
    
    # 成功
    SUCCESS = 0
    
    # 卡密相关错误
    CARD_ERROR = 1
    
    # API接口未启用
    API_DISABLED = 2
    
    # 系统错误
    SYSTEM_ERROR = 3
    
    # API密钥无效
    INVALID_API_KEY = 4
    
    # 卡密已被禁用
    CARD_DISABLED = 5


class ApiErrorMessages:
    """API错误消息常量类"""
    
    # 中文错误消息
    MESSAGES_ZH = {
        ApiErrorCode.SUCCESS: "成功",
        ApiErrorCode.CARD_ERROR: "卡密相关错误",
        ApiErrorCode.API_DISABLED: "API接口未启用",
        ApiErrorCode.SYSTEM_ERROR: "系统错误",
        ApiErrorCode.INVALID_API_KEY: "API密钥无效",
        ApiErrorCode.CARD_DISABLED: "卡密已被禁用",
    }
    
    # 英文错误消息
    MESSAGES_EN = {
        ApiErrorCode.SUCCESS: "Success",
        ApiErrorCode.CARD_ERROR: "Card related error",
        ApiErrorCode.API_DISABLED: "API interface disabled",
        ApiErrorCode.SYSTEM_ERROR: "System error",
        ApiErrorCode.INVALID_API_KEY: "Invalid API key",
        ApiErrorCode.CARD_DISABLED: "Card disabled",
    }
    
    # 详细错误描述
    DESCRIPTIONS = {
        ApiErrorCode.SUCCESS: "请求成功，可以正常处理返回的数据",
        ApiErrorCode.CARD_ERROR: "可能的错误原因：卡密不存在、卡密已被其他设备使用、未提供卡密或设备ID",
        ApiErrorCode.API_DISABLED: "请联系管理员启用API接口",
        ApiErrorCode.SYSTEM_ERROR: "服务器内部错误，请稍后重试或联系管理员",
        ApiErrorCode.INVALID_API_KEY: "请检查API密钥是否正确或是否已被禁用",
        ApiErrorCode.CARD_DISABLED: "此卡密已被管理员手动禁用，请联系管理员处理",
    }


class ApiHttpStatus:
    """API HTTP状态码映射类"""
    
    STATUS_MAPPING = {
        ApiErrorCode.SUCCESS: status.HTTP_200_OK,
        ApiErrorCode.CARD_ERROR: status.HTTP_400_BAD_REQUEST,
        ApiErrorCode.API_DISABLED: status.HTTP_403_FORBIDDEN,
        ApiErrorCode.SYSTEM_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ApiErrorCode.INVALID_API_KEY: status.HTTP_401_UNAUTHORIZED,
        ApiErrorCode.CARD_DISABLED: status.HTTP_403_FORBIDDEN,
    }


class ApiResponse:
    """API响应构建器类"""
    
    @staticmethod
    def success(data=None, message=None):
        """构建成功响应"""
        response_data = {
            'code': ApiErrorCode.SUCCESS,
            'success': True,
            'message': message or ApiErrorMessages.MESSAGES_ZH[ApiErrorCode.SUCCESS]
        }
        
        if data is not None:
            response_data['data'] = data
            
        return response_data
    
    @staticmethod
    def error(error_code, message=None, data=None):
        """构建错误响应"""
        response_data = {
            'code': error_code,
            'success': False,
            'message': message or ApiErrorMessages.MESSAGES_ZH.get(error_code, '未知错误')
        }
        
        if data is not None:
            response_data['data'] = data
            
        return response_data
    
    @staticmethod
    def card_not_found():
        """卡密不存在错误"""
        return ApiResponse.error(
            ApiErrorCode.CARD_ERROR,
            "卡密不存在"
        )
    
    @staticmethod
    def card_expired():
        """卡密已过期错误"""
        return ApiResponse.error(
            ApiErrorCode.CARD_ERROR,
            "卡密已过期"
        )
    
    @staticmethod
    def card_used_up():
        """卡密已用完错误"""
        return ApiResponse.error(
            ApiErrorCode.CARD_ERROR,
            "卡密使用次数已用完"
        )
    
    @staticmethod
    def card_disabled():
        """卡密已被禁用错误"""
        return ApiResponse.error(
            ApiErrorCode.CARD_DISABLED,
            "卡密已被禁用"
        )
    
    @staticmethod
    def device_limit_exceeded():
        """设备数量超限错误"""
        return ApiResponse.error(
            ApiErrorCode.CARD_ERROR,
            "设备绑定数量已达上限"
        )
    
    @staticmethod
    def device_already_bound():
        """设备已被其他卡密绑定错误"""
        return ApiResponse.error(
            ApiErrorCode.CARD_ERROR,
            "设备已被其他卡密绑定"
        )
    
    @staticmethod
    def invalid_api_key():
        """API密钥无效错误"""
        return ApiResponse.error(
            ApiErrorCode.INVALID_API_KEY,
            "API密钥无效或已被禁用"
        )
    
    @staticmethod
    def missing_parameters(missing_params):
        """缺少必要参数错误"""
        return ApiResponse.error(
            ApiErrorCode.CARD_ERROR,
            f"缺少必要参数: {', '.join(missing_params)}"
        )
    
    @staticmethod
    def system_error(error_message=None):
        """系统错误"""
        return ApiResponse.error(
            ApiErrorCode.SYSTEM_ERROR,
            error_message or "系统内部错误"
        )


def get_http_status(error_code):
    """根据错误码获取HTTP状态码"""
    return ApiHttpStatus.STATUS_MAPPING.get(error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


def format_api_response(error_code, message=None, data=None):
    """格式化API响应（兼容旧版本）"""
    if error_code == ApiErrorCode.SUCCESS:
        return ApiResponse.success(data, message)
    else:
        return ApiResponse.error(error_code, message, data)


# 常用错误响应快捷方式
CARD_NOT_FOUND = ApiResponse.card_not_found()
CARD_EXPIRED = ApiResponse.card_expired()
CARD_USED_UP = ApiResponse.card_used_up()
CARD_DISABLED = ApiResponse.card_disabled()
INVALID_API_KEY = ApiResponse.invalid_api_key()
SYSTEM_ERROR = ApiResponse.system_error()
