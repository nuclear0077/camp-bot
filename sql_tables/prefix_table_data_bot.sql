/****** Object:  Table [dbo].[prefix_table_data_bot]    Script Date: 09.05.2022 19:22:57 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[prefix_table_data_bot](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Type_Traning_id] [int] NOT NULL,
	[Faculties_id] [int] NOT NULL,
	[Directions_id] [int] NOT NULL,
	[Description] [nvarchar](max) NOT NULL,
	[Img] [varchar](max) NULL,
 CONSTRAINT [PK_prefix_table_data_id] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


