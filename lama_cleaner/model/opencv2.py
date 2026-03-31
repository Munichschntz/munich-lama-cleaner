import cv2
from lama_cleaner.model.base import InpaintModel
from lama_cleaner.schema import Config

CV2_FLAG_MAP = {
    "INPAINT_NS": cv2.INPAINT_NS,
    "INPAINT_TELEA": cv2.INPAINT_TELEA,
}

class OpenCV2(InpaintModel):
    pad_mod = 1

    @staticmethod
    def is_downloaded() -> bool:
        return True

    def forward(self, image, mask, config: Config):
        """Input image and output image have same size
        image: [H, W, C] RGB
        mask: [H, W, 1]
        return: BGR IMAGE
        """
        flag = CV2_FLAG_MAP.get(config.cv2_flag, cv2.INPAINT_TELEA)
        cur_res = cv2.inpaint(
            image[:, :, ::-1],
            mask,
            inpaintRadius=config.cv2_radius,
            flags=flag,
        )
        return cur_res
