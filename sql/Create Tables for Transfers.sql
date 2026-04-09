/****************************************
[dbo].[tblTransferRequest]
****************************************/
CREATE TABLE [dbo].[tblTransferRequest](
	[RequestID] [int] IDENTITY(1,1) NOT NULL,
	[ProjectNumber] [varchar](5) NULL,
	--[VreNumber] [varchar](15) NULL,
	[RequestType] [int] NOT NULL,
	[RequestedBy] [int] NULL,
	[RequesterNotes] [varchar](max) NULL,
	[ReviewedBy] [int] NULL,
	[ReviewDate] [datetime] NULL,
	[ReviewNotes] [varchar](max) NULL,
	[TransferMethod] [int] NULL,
	[TransferFrom] [varchar](250) NULL,
	[TransferTo] [varchar](250) NULL,
	[DsaReviewed] [int] NULL,
	[ValidFrom] [datetime] NULL,
	[ValidTo] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_TransferRequest] PRIMARY KEY CLUSTERED 
(
	[RequestID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO

ALTER TABLE [dbo].[tblTransferRequest] ADD  DEFAULT (getdate()) FOR [ReviewDate]
GO

ALTER TABLE [dbo].[tblTransferRequest] ADD  DEFAULT (getdate()) FOR [ValidFrom]
GO

ALTER TABLE [dbo].[tblTransferRequest] ADD  DEFAULT (suser_sname()) FOR [CreatedBy]
GO

ALTER TABLE [dbo].[tblTransferRequest]  WITH NOCHECK ADD  CONSTRAINT [FK_tblTransferRequest_FileTransferMethods] FOREIGN KEY([TransferMethod])
REFERENCES [dbo].[tlkFileTransferMethods] ([MethodID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[tblTransferRequest] CHECK CONSTRAINT [FK_tblTransferRequest_FileTransferMethods]
GO

ALTER TABLE [dbo].[tblTransferRequest]  WITH CHECK ADD  CONSTRAINT [FK_TransferRequest_RequestTypes] FOREIGN KEY([RequestType])
REFERENCES [dbo].[tlkTransferRequestTypes] ([RequestTypeID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[tblTransferRequest] CHECK CONSTRAINT [FK_TransferRequest_RequestTypes]
GO


/****************************************
[dbo].[tblTransferFileAsset]
****************************************/
CREATE TABLE [dbo].[tblTransferFileAsset](
	[AssetID] [int] IDENTITY(1,1) NOT NULL,
	[AssetName] [varchar](500) NULL,
	--[DataOwner] [varchar](100) NULL,
	--[ValidFrom] [datetime] NULL,
	--[ValidTo] [datetime] NULL,
	--[CreatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_TransferFileAsset] PRIMARY KEY CLUSTERED 
(
	[AssetID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

--ALTER TABLE [dbo].[tblTransferFileAsset] ADD  DEFAULT (getdate()) FOR [ValidFrom]
--GO

--ALTER TABLE [dbo].[tblTransferFileAsset] ADD  DEFAULT (suser_sname()) FOR [CreatedBy]
--GO


/****************************************
[dbo].[tblTransferFile]
****************************************/
CREATE TABLE [dbo].[tblTransferFile](
	[FileID] [int] IDENTITY(1,1) NOT NULL,
	[RequestID] [int] NOT NULL,
	[FileName] [varchar](300) NOT NULL,
	[TreFilePath] [varchar](200) NULL,
	[DataRepoFilePath] [varchar](200) NULL,
	[TransferAccepted] [bit] NULL,
	[RejectionNotes] [varchar](max) NULL,
	[AssetID] [int] NULL,
	[ValidFrom] [datetime] NULL,
	[ValidTo] [datetime] NULL,
	[CreatedBy] [varchar](50) NULL,
 CONSTRAINT [PK_TransferFile] PRIMARY KEY CLUSTERED 
(
	[FileID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[tblTransferFile] ADD  DEFAULT ((1)) FOR [TransferAccepted]
GO

ALTER TABLE [dbo].[tblTransferFile] ADD  DEFAULT (getdate()) FOR [ValidFrom]
GO

ALTER TABLE [dbo].[tblTransferFile] ADD  DEFAULT (suser_sname()) FOR [CreatedBy]
GO

ALTER TABLE [dbo].[tblTransferFile]  WITH NOCHECK ADD  CONSTRAINT [FK_TransferFile_TransferRequest] FOREIGN KEY([RequestID])
REFERENCES [dbo].[tblTransferRequest] ([RequestID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[tblTransferFile] CHECK CONSTRAINT [FK_TransferFile_TransferRequest]
GO

ALTER TABLE [dbo].[tblTransferFile]  WITH NOCHECK ADD  CONSTRAINT [FK_TransferFile_TransferFileAsset] FOREIGN KEY([AssetID])
REFERENCES [dbo].[tblTransferFileAsset] ([AssetID])
ON UPDATE CASCADE
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[tblTransferFile] CHECK CONSTRAINT [FK_TransferFile_TransferFileAsset]
GO
