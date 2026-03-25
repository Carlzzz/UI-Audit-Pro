/** 与报告页缩略图一致的留白 */
const THUMB_PAD = 80
/** 导出缩略图最大边，避免超大 base64 导致导出耗时过长 */
const MAX_EXPORT_THUMB_EDGE = 900

/**
 * 从整页截图中裁剪出问题区域（含红框），返回 PNG data URL
 */
export function cropIssueFromScreenshot(base64Png, rect, pad = THUMB_PAD) {
  return new Promise((resolve) => {
    if (!base64Png || !rect || rect.width <= 0 || rect.height <= 0) {
      resolve(null)
      return
    }
    const raw = String(base64Png).replace(/^data:image\/\w+;base64,/, '')
    const img = new Image()
    img.onload = () => {
      const W = img.naturalWidth
      const H = img.naturalHeight
      const sx = Math.max(0, Math.floor(rect.left - pad))
      const sy = Math.max(0, Math.floor(rect.top - pad))
      const cw = Math.min(W - sx, Math.ceil(rect.width + 2 * pad))
      const ch = Math.min(H - sy, Math.ceil(rect.height + 2 * pad))
      if (cw <= 1 || ch <= 1) {
        resolve(null)
        return
      }
      const canvas = document.createElement('canvas')
      canvas.width = cw
      canvas.height = ch
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, sx, sy, cw, ch, 0, 0, cw, ch)
      const bx = rect.left - sx
      const by = rect.top - sy
      ctx.strokeStyle = '#ef4444'
      ctx.lineWidth = 2
      ctx.strokeRect(bx, by, rect.width, rect.height)
      if (Math.max(cw, ch) <= MAX_EXPORT_THUMB_EDGE) {
        resolve(canvas.toDataURL('image/png'))
        return
      }
      // 大图下采样：显著减少导出体积与编码时间，同时保持截图可读性
      const scale = MAX_EXPORT_THUMB_EDGE / Math.max(cw, ch)
      const out = document.createElement('canvas')
      out.width = Math.max(1, Math.round(cw * scale))
      out.height = Math.max(1, Math.round(ch * scale))
      const octx = out.getContext('2d')
      octx.drawImage(canvas, 0, 0, out.width, out.height)
      resolve(out.toDataURL('image/png'))
    }
    img.onerror = () => resolve(null)
    img.src = 'data:image/png;base64,' + raw
  })
}

function dataUrlToUint8Array(dataUrl) {
  const base64 = dataUrl.split(',')[1]
  const binary = atob(base64)
  const len = binary.length
  const bytes = new Uint8Array(len)
  for (let i = 0; i < len; i++) bytes[i] = binary.charCodeAt(i)
  return bytes
}

/**
 * 将 DOM 转为多页 PDF（中文由页面字体渲染进位图，避免 jsPDF 缺中文字体）
 */
export async function downloadPdfFromElement(element, filename = '走查报告.pdf', options = {}) {
  const html2canvas = (await import('html2canvas')).default
  const { jsPDF } = await import('jspdf')
  const onProgress = typeof options?.onProgress === 'function' ? options.onProgress : null
  const renderScale = Number(options?.scale) > 0 ? Number(options.scale) : 1.5
  const pagedEls = Array.from(element.querySelectorAll('.rep-ex-page'))
  if (pagedEls.length > 0) {
    const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' })
    const pageWidth = pdf.internal.pageSize.getWidth()
    const pageHeight = pdf.internal.pageSize.getHeight()
    const margin = 8
    const imgWidth = pageWidth - 2 * margin
    const imgMaxHeight = pageHeight - 2 * margin
    for (let i = 0; i < pagedEls.length; i++) {
      const pageEl = pagedEls[i]
      const canvas = await html2canvas(pageEl, {
        scale: renderScale,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        width: pageEl.scrollWidth,
        height: pageEl.scrollHeight,
      })
      const pageImgData = canvas.toDataURL('image/png', 1.0)
      const naturalHeight = (canvas.height * imgWidth) / canvas.width
      const drawHeight = Math.min(imgMaxHeight, naturalHeight)
      if (i > 0) pdf.addPage()
      pdf.addImage(pageImgData, 'PNG', margin, margin, imgWidth, drawHeight, undefined, 'FAST')
      if (onProgress) onProgress((i + 1) / pagedEls.length)
    }
    pdf.save(filename)
    return
  }

  const safeBreaks = []
  const rootTop = element.getBoundingClientRect().top
  element.querySelectorAll('.rep-ex-table tr, .rep-ex-block, .rep-ex-score-card').forEach((node) => {
    const rect = node.getBoundingClientRect()
    const start = Math.max(0, Math.round(rect.top - rootTop))
    const end = Math.max(0, Math.round(rect.bottom - rootTop))
    safeBreaks.push(start, end)
  })
  const canvas = await html2canvas(element, {
    scale: renderScale,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
    width: element.scrollWidth,
    height: element.scrollHeight,
  })
  const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' })
  const pageWidth = pdf.internal.pageSize.getWidth()
  const pageHeight = pdf.internal.pageSize.getHeight()
  const margin = 10
  const imgWidth = pageWidth - 2 * margin
  const maxSliceHeightPx = Math.floor((canvas.width * (pageHeight - margin * 2)) / imgWidth)
  const sortedBreaks = [...new Set(safeBreaks)].sort((a, b) => a - b)
  let y = 0
  let firstPage = true
  while (y < canvas.height) {
    let nextY = Math.min(canvas.height, y + maxSliceHeightPx)
    const candidate = sortedBreaks
      .filter((v) => v > y + Math.floor(maxSliceHeightPx * 0.6) && v < nextY)
      .pop()
    if (candidate) nextY = candidate
    const sliceH = Math.max(1, nextY - y)
    const pageCanvas = document.createElement('canvas')
    pageCanvas.width = canvas.width
    pageCanvas.height = sliceH
    const pageCtx = pageCanvas.getContext('2d')
    pageCtx.drawImage(canvas, 0, y, canvas.width, sliceH, 0, 0, canvas.width, sliceH)
    const pageImgData = pageCanvas.toDataURL('image/png', 1.0)
    const pageImgHeight = (sliceH * imgWidth) / canvas.width
    if (!firstPage) pdf.addPage()
    pdf.addImage(pageImgData, 'PNG', margin, margin, imgWidth, pageImgHeight, undefined, 'FAST')
    y = nextY
    firstPage = false
    if (onProgress) onProgress(Math.min(1, y / canvas.height))
  }

  pdf.save(filename)
}

/**
 * 整页长图导出 JPG / PNG
 */
export async function downloadImageFromElement(element, mime = 'image/png', filename = '走查报告.png') {
  const html2canvas = (await import('html2canvas')).default
  const { saveAs } = await import('file-saver')
  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    logging: false,
    backgroundColor: '#ffffff',
    width: element.scrollWidth,
    height: element.scrollHeight,
  })
  const type = mime === 'image/jpeg' ? 'image/jpeg' : 'image/png'
  const quality = type === 'image/jpeg' ? 0.92 : undefined
  await new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          reject(new Error('toBlob failed'))
          return
        }
        saveAs(blob, filename)
        resolve()
      },
      type,
      quality
    )
  })
}

/**
 * Word：文字 + 每问截图嵌入
 */
function dataUrlImageSize(dataUrl) {
  return new Promise((resolve) => {
    const i = new Image()
    i.onload = () => resolve({ w: i.naturalWidth, h: i.naturalHeight })
    i.onerror = () => resolve({ w: 400, h: 280 })
    i.src = dataUrl
  })
}

export async function exportReportDocx({ reportData, issues, diagnosisPlain, modeLabel, issueThumbMap = {}, totalScore }) {
  const {
    Document,
    Packer,
    Paragraph,
    TextRun,
    ImageRun,
    HeadingLevel,
    Table,
    TableRow,
    TableCell,
    WidthType,
    VerticalAlign,
  } = await import('docx')
  const { saveAs } = await import('file-saver')

  const children = []
  children.push(
    new Paragraph({
      text: '自动化走查平台 · 走查报告',
      heading: HeadingLevel.TITLE,
    })
  )
  children.push(
    new Paragraph({
      children: [new TextRun(`目标页面：${reportData?.url || '—'}`)],
    })
  )
  children.push(
    new Paragraph({
      children: [new TextRun(`走查模式：${modeLabel || reportData?.mode || '—'}`)],
    })
  )
  children.push(
    new Paragraph({
      children: [new TextRun(`问题数量：${issues?.length ?? 0}`)],
    })
  )
  children.push(
    new Paragraph({
      children: [new TextRun(`总还原度：${totalScore ?? reportData?.score ?? '—'} 分`)],
    })
  )
  const counts = { visual: 0, interaction: 0, content: 0, functional: 0 }
  for (const issue of issues || []) {
    const t = String(issue?.category || '').toLowerCase()
    if (t.includes('visual') || t.includes('视觉')) counts.visual++
    else if (t.includes('interaction') || t.includes('交互')) counts.interaction++
    else if (t.includes('content') || t.includes('文案')) counts.content++
    else counts.functional++
  }
  const total = (issues || []).length || 1
  children.push(new Paragraph({ children: [new TextRun({ text: '关键问题分布', bold: true })] }))
  children.push(new Paragraph({ children: [new TextRun(`视觉一致性：${counts.visual} 个 (${Math.round((counts.visual / total) * 100)}%)`)] }))
  children.push(new Paragraph({ children: [new TextRun(`交互体验：${counts.interaction} 个 (${Math.round((counts.interaction / total) * 100)}%)`)] }))
  children.push(new Paragraph({ children: [new TextRun(`文案与话术：${counts.content} 个 (${Math.round((counts.content / total) * 100)}%)`)] }))
  children.push(new Paragraph({ children: [new TextRun(`功能障碍：${counts.functional} 个 (${Math.round((counts.functional / total) * 100)}%)`)] }))
  if (diagnosisPlain) {
    children.push(new Paragraph({ children: [new TextRun({ text: 'AI 诊断结论', bold: true })] }))
    diagnosisPlain
      .split(/\n+/)
      .flatMap((line) => line.split(/[•·]/g))
      .forEach((line) => {
        const t = line.replace(/^[•\-\*]\s*/, '').replace(/\*\*/g, '').trim()
        if (t) children.push(new Paragraph({ children: [new TextRun(t)] }))
      })
  }

  const screenshot = reportData?.screenshot || ''
  children.push(new Paragraph({ children: [new TextRun({ text: '问题清单（表格）', bold: true })] }))

  const rows = []
  rows.push(
    new TableRow({
      tableHeader: true,
      children: [
        new TableCell({ width: { size: 7, type: WidthType.PERCENTAGE }, children: [new Paragraph({ children: [new TextRun({ text: '序号', bold: true })] })] }),
        new TableCell({ width: { size: 25, type: WidthType.PERCENTAGE }, children: [new Paragraph({ children: [new TextRun({ text: '问题截图', bold: true })] })] }),
        new TableCell({ width: { size: 20, type: WidthType.PERCENTAGE }, children: [new Paragraph({ children: [new TextRun({ text: '问题标题', bold: true })] })] }),
        new TableCell({ width: { size: 24, type: WidthType.PERCENTAGE }, children: [new Paragraph({ children: [new TextRun({ text: '问题描述', bold: true })] })] }),
        new TableCell({ width: { size: 24, type: WidthType.PERCENTAGE }, children: [new Paragraph({ children: [new TextRun({ text: '修复建议', bold: true })] })] }),
      ],
    })
  )

  for (let i = 0; i < (issues || []).length; i++) {
    const issue = issues[i]
    let dataUrl = issueThumbMap?.[issue.id] || ''
    if (!dataUrl && screenshot && issue.rect) {
      dataUrl = await cropIssueFromScreenshot(screenshot, issue.rect)
    }
    let imageParagraph = new Paragraph('无截图')
    if (dataUrl) {
      const buf = dataUrlToUint8Array(dataUrl)
      const { w: iw, h: ih } = await dataUrlImageSize(dataUrl)
      const maxW = 140
      const tw = Math.min(maxW, iw)
      const th = Math.round((tw * ih) / iw)
      imageParagraph = new Paragraph({
        children: [
          new ImageRun({
            data: buf,
            transformation: { width: tw, height: th },
          }),
        ],
      })
    }
    rows.push(
      new TableRow({
        cantSplit: true,
        children: [
          new TableCell({
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph(String(i + 1))],
          }),
          new TableCell({
            children: [imageParagraph],
          }),
          new TableCell({
            children: [new Paragraph(String(issue.title || '（无标题）'))],
          }),
          new TableCell({
            children: [new Paragraph(String(issue.desc || '—'))],
          }),
          new TableCell({
            children: [new Paragraph(String(issue.suggestion || '—'))],
          }),
        ],
      })
    )
  }

  children.push(
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      rows,
    })
  )

  const doc = new Document({
    sections: [
      {
        children,
      },
    ],
  })
  const blob = await Packer.toBlob(doc)
  saveAs(blob, `走查报告_${Date.now()}.docx`)
}
