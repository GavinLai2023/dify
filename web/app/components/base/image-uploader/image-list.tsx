import type { FC } from 'react'
import { useTranslation } from 'react-i18next'
import { Loading02, XClose } from '@/app/components/base/icons/src/vender/line/general'
import { RefreshCcw01 } from '@/app/components/base/icons/src/vender/line/arrows'
import { AlertTriangle } from '@/app/components/base/icons/src/vender/solid/alertsAndFeedback'
import TooltipPlus from '@/app/components/base/tooltip-plus'
import type { ImageFile } from '@/types/app'
import { TransferMethod } from '@/types/app'
import { useModalContext } from '@/context/modal-context'

type ImageListProps = {
  list: ImageFile[]
  readonly?: boolean
  onRemove?: (imageFileId: string) => void
  onReUpload?: (imageFileId: string) => void
  onImageLinkLoadSuccess?: (imageFileId: string) => void
  onImageLinkLoadError?: (imageFileId: string) => void
}

const ImageList: FC<ImageListProps> = ({
  list,
  readonly,
  onRemove,
  onReUpload,
  onImageLinkLoadSuccess,
  onImageLinkLoadError,
}) => {
  const { t } = useTranslation()
  const { setShowImagePreview } = useModalContext()

  const handleImageLinkLoadSuccess = (item: ImageFile) => {
    if (item.type === TransferMethod.remote_url && onImageLinkLoadSuccess)
      onImageLinkLoadSuccess(item._id)
  }
  const handleImageLinkLoadError = (item: ImageFile) => {
    if (item.type === TransferMethod.remote_url && onImageLinkLoadError)
      onImageLinkLoadError(item._id)
  }

  return (
    <div className='flex'>
      {
        list.map(item => (
          <div
            key={item._id}
            className='group relative mr-1'
          >
            {
              item.type === TransferMethod.local_file && item.progress !== 100 && (
                <div className='absolute inset-0 flex items-center justify-center rounded-lg z-[1] bg-black/30'>
                  {
                    item.progress === -1 && (
                      <RefreshCcw01 className='w-5 h-5 text-white' onClick={() => onReUpload && onReUpload(item._id)} />
                    )
                  }
                </div>
              )
            }
            {
              item.type === TransferMethod.remote_url && item.progress !== 100 && (
                <div className={`
                  absolute inset-0 flex items-center justify-center rounded-lg z-[1] border
                  ${item.progress === -1 ? 'bg-[#FEF0C7] border-[#DC6803]' : 'bg-black/[0.16] border-transparent'}
                `}>
                  {
                    item.progress > -1 && (
                      <Loading02 className='animate-spin w-5 h-5 text-white' />
                    )
                  }
                  {
                    item.progress === -1 && (
                      <TooltipPlus popupContent={t('common.imageUploader.pasteImageLinkInvalid')}>
                        <AlertTriangle className='w-4 h-4 text-[#DC6803]' />
                      </TooltipPlus>
                    )
                  }
                </div>
              )
            }
            <img
              className='w-16 h-16 rounded-lg object-cover cursor-pointer border-[0.5px] border-black/5'
              alt=''
              onLoad={() => handleImageLinkLoadSuccess(item)}
              onError={() => handleImageLinkLoadError(item)}
              src={item.type === TransferMethod.remote_url ? item.url : item.base64Url}
              onClick={() => setShowImagePreview({ payload: (item.type === TransferMethod.remote_url ? item.url : item.base64Url) as string })}
            />
            {
              !readonly && (
                <div
                  className={`
                    absolute z-10 -top-[9px] -right-[9px] items-center justify-center w-[18px] h-[18px] 
                    bg-white hover:bg-gray-50 border-[0.5px] border-black/[0.02] rounded-2xl shadow-lg
                    cursor-pointer
                    ${item.progress === -1 ? 'flex' : 'hidden group-hover:flex'}
                  `}
                  onClick={() => onRemove && onRemove(item._id)}
                >
                  <XClose className='w-3 h-3 text-gray-500' />
                </div>
              )
            }
          </div>
        ))
      }
    </div>
  )
}

export default ImageList