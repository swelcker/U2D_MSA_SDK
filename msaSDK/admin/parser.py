import datetime
from typing import Any, Iterable

from pydantic import Json
from pydantic.fields import ModelField
from pydantic.utils import smart_deepcopy

from msaSDK.admin.frontend.components import (FormItem, Group, InputNumber,
                                              Remark, TableColumn, Validation)
from msaSDK.admin.frontend.constants import LabelEnum
from msaSDK.admin.utils.choices import MSAChoices
from msaSDK.admin.utils.translation import i18n as _


class MSAUIParser:
    """MSA UI Core Model Parser"""

    def __init__(self, modelfield: ModelField):
        self.modelfield = modelfield  # read only

    @property
    def label(self):
        return self.modelfield.field_info.title or self.modelfield.name

    @property
    def remark(self):
        return (
            Remark(content=self.modelfield.field_info.description)
            if self.modelfield.field_info.description
            else None
        )

    def as_form_item(
        self, set_default: bool = False, is_filter: bool = False
    ) -> FormItem:
        formitem = self._parse_form_item_from_kwargs(is_filter)
        if not is_filter:
            if self.modelfield.field_info.max_length:
                formitem.maxLength = self.modelfield.field_info.max_length
            if self.modelfield.field_info.min_length:
                formitem.minLength = self.modelfield.field_info.min_length
            formitem.required = self.modelfield.required and not issubclass(
                self.modelfield.type_, bool
            )
            if set_default:
                formitem.value = self.modelfield.default
        formitem.name = self.modelfield.alias
        formitem.label = formitem.label or self.label
        formitem.labelRemark = formitem.labelRemark or self.remark
        if formitem.type in {"input-image", "input-file"}:
            formitem = Group(
                name=formitem.name,
                body=[
                    formitem,
                    formitem.copy(
                        exclude={"maxLength", "receiver"},
                        update={"type": "input-text"},
                    ),
                ],
            )
        return formitem

    def as_table_column(self, quick_edit: bool = False) -> TableColumn:
        column = self._parse_table_column_from_kwargs()
        column.name = self.modelfield.alias
        column.label = column.label or self.label
        column.remark = column.remark or self.remark
        column.sortable = True
        if column.type in ["text", None]:
            column.searchable = True
        elif column.type in ["switch", "mapping"]:
            column.sortable = False
        if quick_edit:
            column.quickEdit = self.as_form_item(set_default=True).dict(
                exclude_none=True, by_alias=True, exclude={"name", "label"}
            )
            column.quickEdit.update({"saveImmediately": True})
            if column.quickEdit.get("type") == "switch":
                column.quickEdit.update({"mode": "inline"})
        return column

    def _parse_form_item_from_kwargs(self, is_filter: bool = False) -> FormItem:
        kwargs = {}
        formitem = self.modelfield.field_info.extra.get(
            ["msa_ui_form_item", "msa_ui_filter_item"][is_filter]
        )
        if formitem is not None:
            formitem = smart_deepcopy(formitem)
            if isinstance(formitem, FormItem):
                pass
            elif isinstance(formitem, dict):
                kwargs = formitem
                formitem = FormItem(**kwargs) if kwargs.get("type") else None
            elif isinstance(formitem, str):
                formitem = FormItem(type=formitem)
            else:
                formitem = None
        if formitem is not None:
            pass
        elif self.modelfield.type_ in [str, Any]:
            kwargs["type"] = "input-text"
        elif issubclass(self.modelfield.type_, MSAChoices):
            kwargs.update(
                {
                    "type": "select",
                    "options": [
                        {"label": l, "value": v}
                        for v, l in self.modelfield.type_.choices
                    ],
                    "extractValue": True,
                    "joinValues": False,
                }
            )
            if not self.modelfield.required:
                kwargs["clearable"] = True
        elif issubclass(self.modelfield.type_, bool):
            kwargs["type"] = "switch"
        elif is_filter:
            if issubclass(self.modelfield.type_, datetime.datetime):
                kwargs["type"] = "input-datetime-range"
                kwargs["format"] = "YYYY-MM-DD HH:mm:ss"
                # 给筛选的 DateTimeRange 添加 today 标签
                kwargs[
                    "ranges"
                ] = "today,yesterday,7daysago,prevweek,thismonth,prevmonth,prevquarter"
            elif issubclass(self.modelfield.type_, datetime.date):
                kwargs["type"] = "input-date-range"
                kwargs["format"] = "YYYY-MM-DD"
            elif issubclass(self.modelfield.type_, datetime.time):
                kwargs["type"] = "input-time-range"
                kwargs["format"] = "HH:mm:ss"
            else:
                kwargs["type"] = "input-text"
        elif issubclass(self.modelfield.type_, int):
            formitem = InputNumber(precision=0, validations=Validation(isInt=True))
        elif issubclass(self.modelfield.type_, float):
            formitem = InputNumber(validations=Validation(isFloat=True))
        elif issubclass(self.modelfield.type_, datetime.datetime):
            kwargs["type"] = "input-datetime"
            kwargs["format"] = "YYYY-MM-DDTHH:mm:ss"
        elif issubclass(self.modelfield.type_, datetime.date):
            kwargs["type"] = "input-date"
            kwargs["format"] = "YYYY-MM-DD"
        elif issubclass(self.modelfield.type_, datetime.time):
            kwargs["type"] = "input-time"
            kwargs["format"] = "HH:mm:ss"
        elif issubclass(self.modelfield.type_, Json):
            kwargs["type"] = "json-editor"
        else:
            kwargs["type"] = "input-text"
        return formitem or FormItem(**kwargs)

    def _parse_table_column_from_kwargs(self) -> TableColumn:
        kwargs = {}
        column = self.modelfield.field_info.extra.get("msa_ui_table_column")
        if column is not None:
            column = smart_deepcopy(column)
            if isinstance(column, TableColumn):
                pass
            elif isinstance(column, dict):
                kwargs = column
                column = TableColumn(**kwargs) if kwargs.get("type") else None
            elif isinstance(column, str):
                column = TableColumn(type=column)
            else:
                column = None
        if column is not None:
            pass
        elif self.modelfield.type_ in [str, Any]:
            pass
        elif issubclass(self.modelfield.type_, bool):
            kwargs["type"] = "switch"
            kwargs["filterable"] = {
                "options": [
                    {"label": _("YES"), "value": True},
                    {"label": _("NO"), "value": False},
                ]
            }
        elif issubclass(self.modelfield.type_, datetime.datetime):
            kwargs["type"] = "datetime"
        elif issubclass(self.modelfield.type_, datetime.date):
            kwargs["type"] = "date"
        elif issubclass(self.modelfield.type_, datetime.time):
            kwargs["type"] = "time"
        elif issubclass(self.modelfield.type_, MSAChoices):
            kwargs["type"] = "mapping"
            kwargs["filterable"] = {
                "options": [
                    {"label": v, "value": k} for k, v in self.modelfield.type_.choices
                ]
            }
            kwargs["map"] = {
                k: f"<span class='label label-{l}'>{v}</span>"
                for (k, v), l in zip(
                    self.modelfield.type_.choices, cyclic_generator(LabelEnum)
                )
            }
        return column or TableColumn(**kwargs)


def cyclic_generator(iterable: Iterable):
    """Yield Iterable"""
    while True:
        yield from iterable
