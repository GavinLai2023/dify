'use client'
import type { FC } from 'react'
import React from 'react'
import cn from 'classnames'
import s from './style.module.css'
import { useModalContext } from '@/context/modal-context'

type Props = {
  srcs: string[]
}

const getWidthStyle = (imgNum: number) => {
  if (imgNum === 1) {
    return {
      maxWidth: '100%',
    }
  }

  if (imgNum === 2 || imgNum === 4) {
    return {
      width: 'calc(50% - 4px)',
    }
  }

  return {
    width: 'calc(33.3333% - 5.3333px)',
  }
}

const ImageGallery: FC<Props> = ({
  srcs,
}) => {
  const { setShowImagePreview } = useModalContext()

  const imgNum = srcs.length
  const imgStyle = getWidthStyle(imgNum)
  return (
    <div className={cn(s[`img-${imgNum}`], 'flex flex-wrap')}>
      {/* TODO: support preview */}
      {srcs.map((src, index) => (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          key={index}
          className={s.item}
          style={imgStyle}
          src={src}
          alt=''
          onClick={() => setShowImagePreview({ payload: src })}
        />
      ))}
    </div>
  )
}

export default React.memo(ImageGallery)

export const ImageGalleryTest = () => {
  const imgGallerySrcs = (() => {
    const srcs = []
    for (let i = 0; i < 6; i++)
      // srcs.push('https://placekitten.com/640/360')
      // srcs.push('https://placekitten.com/360/640')
      srcs.push('https://placekitten.com/360/360')

    return srcs
  })()
  return (
    <div className='space-y-2'>
      {imgGallerySrcs.map((_, index) => (
        <div key={index} className='p-4 pb-2 rounded-lg bg-[#D1E9FF80]'>
          <ImageGallery srcs={imgGallerySrcs.slice(0, index + 1)} />
        </div>
      ))}
    </div>
  )
}