from typing import AbstractSet, Any, Dict, Mapping, Optional, Sequence, Union

from pydantic.fields import Undefined, UndefinedType
from pydantic.typing import NoArgAnyCallable
from sqlalchemy import Column
from sqlmodel.main import FieldInfo

from ..frontend.components import FormItem, TableColumn


def Field(
    default: Any = Undefined,
    *,
    default_factory: Optional[NoArgAnyCallable] = None,
    alias: str = None,
    title: str = None,
    description: str = None,
    exclude: Union[
        AbstractSet[Union[int, str]], Mapping[Union[int, str], Any], Any
    ] = None,
    include: Union[
        AbstractSet[Union[int, str]], Mapping[Union[int, str], Any], Any
    ] = None,
    const: bool = None,
    gt: float = None,
    ge: float = None,
    lt: float = None,
    le: float = None,
    multiple_of: float = None,
    min_items: int = None,
    max_items: int = None,
    min_length: int = None,
    max_length: int = None,
    allow_mutation: bool = True,
    regex: str = None,
    primary_key: bool = False,
    foreign_key: Optional[Any] = None,
    unique: bool = False,
    nullable: Union[bool, UndefinedType] = Undefined,
    index: Union[bool, UndefinedType] = Undefined,
    sa_column: Union[Column, UndefinedType] = Undefined,
    sa_column_args: Union[Sequence[Any], UndefinedType] = Undefined,
    sa_column_kwargs: Union[Mapping[str, Any], UndefinedType] = Undefined,
    schema_extra: Optional[Dict[str, Any]] = None,
    msa_ui_form_item: Union[FormItem, dict, str] = None,
    msa_ui_filter_item: Union[FormItem, dict, str] = None,
    msa_ui_table_column: Union[TableColumn, dict, str] = None,
) -> Any:
    current_schema_extra = schema_extra or {}
    if msa_ui_form_item:
        current_schema_extra["msa_ui_form_item"] = msa_ui_form_item
    if msa_ui_filter_item:
        current_schema_extra["msa_ui_filter_item"] = msa_ui_filter_item
    if msa_ui_table_column:
        current_schema_extra["msa_ui_table_column"] = msa_ui_table_column
    field_info = FieldInfo(
        default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        exclude=exclude,
        include=include,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        min_items=min_items,
        max_items=max_items,
        min_length=min_length,
        max_length=max_length,
        allow_mutation=allow_mutation,
        regex=regex,
        primary_key=primary_key,
        foreign_key=foreign_key,
        unique=unique,
        nullable=nullable,
        index=index,
        sa_column=sa_column,
        sa_column_args=sa_column_args,
        sa_column_kwargs=sa_column_kwargs,
        **current_schema_extra,
    )
    field_info._validate()
    return field_info
