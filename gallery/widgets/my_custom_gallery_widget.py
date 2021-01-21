from typing import Optional
from PySide6 import QtWidgets

from utils.my_custom_widget import MyCustomWidget, MyCustomWidgetMixin
from gallery.models.gallery_models import GalleryModels

class MyCustomGalleryWidget(MyCustomWidget):
    
    models: GalleryModels
    
    @classmethod
    def create_widget(
        cls, parent: Optional[QtWidgets.QWidget] = None
    ) -> MyCustomWidgetMixin:
        widget = super().create_widget(parent)
        if widget._has_parent():
            widget._copy_attribute_from_parent("models")
        return widget