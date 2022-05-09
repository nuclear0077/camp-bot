/****** Object:  Table [dbo].[prefix_table_Directions_bot]    Script Date: 09.05.2022 19:23:42 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[prefix_table_Directions_bot](
	[Id] [int] IDENTITY(1,1) NOT NULL,
	[Type_traning_id] [int] NOT NULL,
	[Faculties_id] [int] NOT NULL,
	[Name] [varchar](max) NULL,
 CONSTRAINT [PK_prefix_table_Directions_tips_id] PRIMARY KEY CLUSTERED 
(
	[Id] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]
GO


