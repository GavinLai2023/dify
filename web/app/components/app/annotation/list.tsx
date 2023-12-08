'use client'
import type { FC } from 'react'
import React from 'react'
import { useTranslation } from 'react-i18next'
import cn from 'classnames'
import dayjs from 'dayjs'
import { Edit02, Trash03 } from '../../base/icons/src/vender/line/general'
import s from './style.module.css'
import type { AnnotationItem } from './type'
import RemoveAnnotationConfirmModal from './remove-annotation-confirm-modal'

type Props = {
  list: AnnotationItem[]
  onRemove: (id: string) => void
}

const List: FC<Props> = ({
  list,
  onRemove,
}) => {
  const { t } = useTranslation()
  const [currId, setCurrId] = React.useState<string | null>(null)
  const [showConfirmDelete, setShowConfirmDelete] = React.useState(false)
  return (
    <div className='overflow-x-auto'>
      <table className={cn(s.logTable, 'w-full min-w-[440px] border-collapse border-0 text-sm')} >
        <thead className="h-8 leading-8 border-b border-gray-200 text-gray-500 font-bold">
          <tr className='uppercase'>
            <td className='whitespace-nowrap'>{t('appAnnotation.table.header.question')}</td>
            <td className='whitespace-nowrap'>{t('appAnnotation.table.header.answer')}</td>
            <td className='whitespace-nowrap'>{t('appAnnotation.table.header.createdAt')}</td>
            <td className='whitespace-nowrap'>{t('appAnnotation.table.header.hits')}</td>
            <td className='whitespace-nowrap w-[96px]'>{t('appAnnotation.table.header.actions')}</td>
          </tr>
        </thead>
        <tbody className="text-gray-500">
          {list.map(item => (
            <tr
              key={item.id}
              className={'border-b border-gray-200 h-8 hover:bg-gray-50 cursor-pointer'}
            >
              <td>{item.question}</td>
              <td>{item.answer}</td>
              <td>{dayjs(item.created_at).format('YYYY-MM-DD hh:mm')}</td>
              <td>{item.hit_count}</td>
              <td className='w-[96px]'>
                {/* Actions */}
                <div className='flex space-x-2 text-gray-500'>
                  <div className='p-1 cursor-pointer rounded-md hover:bg-black/5'>
                    <Edit02 className='w-4 h-4' />
                  </div>
                  <div
                    className='p-1 cursor-pointer rounded-md hover:bg-black/5'
                    onClick={() => {
                      setCurrId(item.id)
                      setShowConfirmDelete(true)
                    }}
                  >
                    <Trash03 className='w-4 h-4' />
                  </div>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <RemoveAnnotationConfirmModal
        isShow={showConfirmDelete}
        onHide={() => setShowConfirmDelete(false)}
        onRemove={() => {
          onRemove(currId as string)
          setShowConfirmDelete(false)
        }}
      />
    </div>
  )
}
export default React.memo(List)
