# coding:utf-8
"""
回测系统数据模型
使用 Pydantic 进行参数验证
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class BacktestConfig(BaseModel):
    """回测配置模型"""
    strategy_path: str = Field(..., description="策略文件路径")
    strategy_class_name: Optional[str] = Field(None, description="策略类名")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    init_cash: float = Field(1000000, gt=0, description="初始资金，必须大于0")
    code: Optional[str] = Field(None, description="回测标的代码")
    frequence: str = Field("1min", description="K线周期")
    timeout: int = Field(3600, gt=0, le=86400, description="超时时间（秒），最大24小时")
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        """验证日期格式"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('日期格式错误，应为 YYYY-MM-DD')
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """验证日期范围"""
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期不能早于开始日期')
        return v
    
    @validator('frequence')
    def validate_frequence(cls, v):
        """验证K线周期"""
        valid_frequences = ['1min', '5min', '15min', '30min', '60min', 'day', 'week', 'month']
        if v not in valid_frequences:
            raise ValueError(f'无效的K线周期，支持: {", ".join(valid_frequences)}')
        return v
    
    @validator('strategy_path')
    def validate_strategy_path(cls, v):
        """验证策略路径"""
        if not v.endswith('.py'):
            raise ValueError('策略文件必须是 .py 文件')
        if '..' in v:
            raise ValueError('策略路径不能包含 ".."')
        return v


class StrategyConfig(BaseModel):
    """策略配置模型"""
    name: str = Field(..., min_length=1, max_length=100, description="策略名称")
    type: str = Field('custom', description="策略类型")
    description: Optional[str] = Field(None, max_length=500, description="策略描述")
    code: Optional[str] = Field(None, description="策略代码")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="策略参数")
    tags: Optional[list] = Field(default_factory=list, description="策略标签")
    
    @validator('type')
    def validate_type(cls, v):
        """验证策略类型"""
        valid_types = ['trend', 'mean_reversion', 'arbitrage', 'hft', 'custom']
        if v not in valid_types:
            raise ValueError(f'无效的策略类型，支持: {", ".join(valid_types)}')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        """验证标签"""
        if v and len(v) > 10:
            raise ValueError('标签数量不能超过10个')
        return v


class BacktestTaskUpdate(BaseModel):
    """回测任务更新模型"""
    status: Optional[str] = Field(None, description="任务状态")
    progress: Optional[int] = Field(None, ge=0, le=100, description="进度 0-100")
    message: Optional[str] = Field(None, max_length=500, description="状态消息")
    
    @validator('status')
    def validate_status(cls, v):
        """验证状态"""
        if v:
            valid_statuses = ['pending', 'running', 'completed', 'failed']
            if v not in valid_statuses:
                raise ValueError(f'无效的状态，支持: {", ".join(valid_statuses)}')
        return v
