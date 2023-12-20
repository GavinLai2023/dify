import type { FC } from 'react'
import { useState } from 'react'
import { useContext } from 'use-context-selector'
import type {
  ModelItem,
  ModelProvider,
} from '../declarations'
import { ConfigurateMethodEnum } from '../declarations'
import {
  DEFAULT_BACKGROUND_COLOR,
  languageMaps,
} from '../utils'
import ModelBadge from '../model-badge'
import CredentialPanel from './credential-panel'
import QuotaPanel from './quota-panel'
import ModelList from './model-list'
import AddModelButton from './add-model-button'
import I18n from '@/context/i18n'
import { ChevronDownDouble } from '@/app/components/base/icons/src/vender/line/arrows'
import { Loading02 } from '@/app/components/base/icons/src/vender/line/general'
import { fetchModelProviderModelList } from '@/service/common'

type ProviderAddedCardProps = {
  provider: ModelProvider
  onOpenModal: (configurateMethod: ConfigurateMethodEnum) => void
}
const ProviderAddedCard: FC<ProviderAddedCardProps> = ({
  provider,
  onOpenModal,
}) => {
  const { locale } = useContext(I18n)
  const language = languageMaps[locale]
  const [fetched, setFetched] = useState(false)
  const [loading, setLoading] = useState(false)
  const [collapsed, setCollapsed] = useState(true)
  const [modelList, setModelList] = useState<ModelItem[]>([])
  const configurateMethods = provider.configurate_methods.filter(method => method !== ConfigurateMethodEnum.fetchFromRemote)
  const systemConfig = provider.system_configuration
  const hasModelList = fetched && !!modelList.length

  const handleOpenModelList = async () => {
    if (fetched) {
      setCollapsed(false)
      return
    }

    try {
      setLoading(true)
      const modelsData = await fetchModelProviderModelList(`/workspaces/current/model-providers/${provider.provider}/models`)
      setModelList(modelsData.data)
      setCollapsed(false)
      setFetched(true)
    }
    finally {
      setLoading(false)
    }
  }

  return (
    <div
      className='mb-2 rounded-xl border-[0.5px] border-black/5 shadow-xs'
      style={{ background: provider.background || DEFAULT_BACKGROUND_COLOR }}
    >
      <div className='flex pl-3 py-2 pr-2 rounded-t-xl'>
        <div className='grow px-1 pt-1 pb-0.5'>
          <div className='mb-2 h-6' style={{ background: provider.icon_large[language] }} />
          <div className='flex gap-0.5'>
            {
              provider.supported_model_types.map(modelType => (
                <ModelBadge
                  key={modelType}
                  text={modelType.toLocaleUpperCase()}
                />
              ))
            }
          </div>
        </div>
        {
          systemConfig.enabled && (
            <QuotaPanel
              provider={provider}
            />
          )
        }
        {
          configurateMethods.includes(ConfigurateMethodEnum.predefinedModel) && (
            <CredentialPanel
              onSetup={() => onOpenModal(ConfigurateMethodEnum.predefinedModel)}
              provider={provider}
            />
          )
        }
      </div>
      {
        collapsed && (
          <div className='group flex items-center justify-between pl-2 py-1.5 pr-[11px] border-t border-t-black/5 bg-white/30 text-xs font-medium text-gray-500'>
            <div className='group-hover:hidden pl-1 pr-1.5 h-6 leading-6'>
              {
                hasModelList
                  ? `${modelList.length} Models`
                  : 'Show Models'
              }
            </div>
            <div
              className='hidden group-hover:flex items-center pl-1 pr-1.5 h-6 rounded-lg hover:bg-white cursor-pointer'
              onClick={handleOpenModelList}
            >
              <ChevronDownDouble className='mr-0.5 w-3 h-3' />
              {
                hasModelList
                  ? `Show ${modelList.length} Models`
                  : 'Show Models'
              }
              {
                loading && (
                  <Loading02 className='ml-0.5 animate-spin w-3 h-3' />
                )
              }
            </div>
            {
              configurateMethods.includes(ConfigurateMethodEnum.customizableModel) && (
                <AddModelButton
                  onClick={() => {}}
                  className='hidden group-hover:flex group-hover:text-primary-600'
                />
              )
            }
          </div>
        )
      }
      {
        !collapsed && (
          <ModelList
            provider={provider}
            models={modelList}
            onCollapse={() => setCollapsed(true)}
          />
        )
      }
    </div>
  )
}

export default ProviderAddedCard